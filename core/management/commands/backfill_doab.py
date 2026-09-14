"""
backfill_doab — gentle, resumable, observable DOAB ID-list backfill.

One-off catch-up command for IDs the nightly `load_doab` cron missed (because
its 3-day rolling window can't self-heal records modified during a stretch of
HTTP 429s). The worklist is auto-discovered (DOAB OAI ListIdentifiers diffed
against the local DB) when --ids-file is omitted, or supplied explicitly for
targeted re-runs. IDs are processed with rate-limited, ID-keyed state and a
4-way per-record outcome taxonomy.

Discovery also emits the *raw* OAI active + deleted sets as `.active` and
`.deleted` artifacts alongside the per-host worklist. A sister host can
consume these via `--use-active-file [--use-deleted-file]` to skip the
~17-min OAI crawl and diff the snapshot against its own local DB. This lets
the regluit fleet (test, dj42, prod) share one DOAB OAI crawl instead of
running three.

Design context: Gluejar/regluit#1151. Reuses `add_by_doab` (idempotent), the
existing pyoai client / OAI-prefix stripper, and the shared Retry-After
sentinel from `load_doab.py` so a 429 hit by discovery, the per-record loop,
or the nightly cron suppresses the others for the duration of the ban.
"""

import argparse
import datetime
import hashlib
import json
import logging
import os
import random
import re
import sys
import time
import traceback
import urllib.error

from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError

from regluit.core.loaders import doab
from regluit.core.management.commands.load_doab import (
    SENTINEL_PATH,
    _now_utc,
    clear_sentinel,
    read_block_deadline,
    write_block_deadline,
)

try:
    from oaipmh.client import RateLimitedError as _PyOAIRateLimitedError
except ImportError:
    class _PyOAIRateLimitedError(Exception):
        retry_after_seconds = None
        retry_after_raw = None

from oaipmh.error import NoRecordsMatchError

logger = logging.getLogger(__name__)

# Terminal statuses (won't re-attempt)
TERMINAL = ('ok', 'gone', 'present_locally', 'error_review')
# Non-terminal: 'retry' (will re-attempt on next run); absent = not yet attempted

# Process exit codes — consumed by the orchestration runner so it can tell
# "done" from "safe to re-invoke next tick" from "stop, a human must look".
#   0  drained / nothing-to-do  -> runner writes .done
#   3  benign checkpoint (rate-limit, max-remote-calls, transient) -> re-fire
#   4  circuit-breaker halt (error/gone rate, unknown) -> runner freezes
EXIT_OK = 0
EXIT_CHECKPOINT = 3
EXIT_HALT = 4
HALT_REASONS = frozenset({
    'error_rate_halt', 'gone_rate_halt',
    'unknown_http_error_halt', 'unknown_exception_halt',
})

# Default fallback when DOAB sends 429 without a parseable Retry-After.
DEFAULT_RETRY_AFTER_SECS = 60

ID_RE = re.compile(r'^20\.500\.12854/(\d+)(?:\.\d+)?$')


# --- ID parsing ---------------------------------------------------------------

def numeric_suffix(doab_id):
    """Parse the integer suffix after `20.500.12854/` for sorting."""
    m = ID_RE.match(doab_id)
    if not m:
        return -1
    return int(m.group(1))


def load_input_ids(path):
    """Read + dedupe + validate. Returns (ids_list, sha256, malformed_lines)."""
    h = hashlib.sha256()
    seen = set()
    ids = []
    malformed = []
    with open(path, 'rb') as f:
        raw_bytes = f.read()
    h.update(raw_bytes)
    for lineno, raw in enumerate(raw_bytes.decode('utf-8').splitlines(), start=1):
        s = raw.strip()
        if not s or s.startswith('#'):
            continue
        if not ID_RE.match(s):
            malformed.append((lineno, raw))
            continue
        if s in seen:
            continue
        seen.add(s)
        ids.append(s)
    return ids, h.hexdigest(), malformed


# --- State management ---------------------------------------------------------

def load_state(path):
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def save_state(path, state):
    """Atomic write via tmp + os.replace so a crash never leaves partial JSON."""
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, 'w') as f:
        json.dump(state, f, indent=2, sort_keys=True)
    os.replace(tmp, path)


def recompute_totals(state):
    """Recompute totals from the ids dict — single source of truth, no drift."""
    counts = {s: 0 for s in TERMINAL + ('retry',)}
    for entry in state['ids'].values():
        st = entry.get('status')
        if st in counts:
            counts[st] += 1
    counts['remaining'] = state['ids_file_count'] - sum(
        counts[s] for s in TERMINAL
    )
    state['totals'] = counts


def init_state(ids_file_path, ids_count, ids_sha256):
    return {
        'started_at': _now_utc().isoformat(),
        'ids_file_path': ids_file_path,
        'ids_file_sha256': ids_sha256,
        'ids_file_count': ids_count,
        'ids': {},
        'totals': dict(
            {s: 0 for s in TERMINAL + ('retry',)},
            remaining=ids_count,
        ),
        'last_run': None,
    }


# --- Per-record outcomes ------------------------------------------------------

def _now_iso():
    return _now_utc().isoformat()


def mark_terminal(state, doab_id, status, **extras):
    entry = state['ids'].get(doab_id, {})
    entry['status'] = status
    entry['last_attempt_at'] = _now_iso()
    entry['attempts'] = entry.get('attempts', 0) + 1
    entry.update(extras)
    state['ids'][doab_id] = entry


def mark_retry(state, doab_id, last_error):
    entry = state['ids'].get(doab_id, {})
    entry['status'] = 'retry'
    entry['last_attempt_at'] = _now_iso()
    entry['attempts'] = entry.get('attempts', 0) + 1
    entry['last_error'] = last_error
    state['ids'][doab_id] = entry


# --- Pacing -------------------------------------------------------------------

def jittered_sleep(rate, jitter):
    if rate <= 0:
        return
    lo = rate * (1 - jitter)
    hi = rate * (1 + jitter)
    time.sleep(random.uniform(lo, hi))


# --- Worklist discovery (Option B) -------------------------------------------

# Conservative fallback if a 429 during discovery carries no parseable
# Retry-After. Larger than the per-record DEFAULT_RETRY_AFTER_SECS because a
# discovery 429 means DOAB wants us off the OAI endpoint entirely for a while.
DISCOVERY_RATE_LIMIT_FALLBACK_SECS = 3600


def derive_cache_paths(state_file):
    """Worklist + side-report + raw-OAI-snapshot paths, co-located with the
    state file.

    The 5 paths are:
      .ids       — per-host backfill worklist (active - local), SHA-pinned
      .stale     — per-host: local & deleted (DOAB-deleted, still local)
      .orphans   — per-host: local - active - deleted (absent from OAI)
      .active    — raw OAI active set, ~125k IDs; reusable across machines
      .deleted   — raw OAI deleted set; companion to .active for accurate
                   stale/orphan reports when reused on another host

    The first three are host-specific (they depend on the local Identifier
    table). The last two are universal — the same DOAB OAI snapshot regardless
    of which machine crawled it — and exist so a sister host can reuse the
    expensive crawl via --use-active-file / --use-deleted-file.
    """
    return (state_file + '.ids',
            state_file + '.stale',
            state_file + '.orphans',
            state_file + '.active',
            state_file + '.deleted')


def atomic_write_lines(path, lines):
    """Same crash-safe tmp+replace discipline as save_state()."""
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, 'w') as f:
        for line in lines:
            f.write(line + '\n')
    os.replace(tmp, path)


def discover_missing_ids(ids_out, stale_out, orphan_out, active_out, deleted_out,
                         stdout, stderr):
    """Crawl DOAB OAI ListIdentifiers, diff against the local DB, write 5
    sorted artifacts; return the count of missing IDs (0 = local in sync).

    Three of the artifacts are host-specific (worklist, stale, orphan) and two
    are the raw OAI snapshot (active, deleted) so a sister host can reuse the
    crawl work via --use-active-file (see discover_via_active_file).

    Single-pass (B1/B3): a 429 mid-crawl writes the *shared* sentinel and
    aborts via CommandError; the next invocation re-crawls from scratch.
    The completed .ids file is then SHA-pinned by the normal load path, so
    discovery runs once and a resumed backfill never re-crawls.

    Reuses the existing pyoai client, the OAI-prefix stripper, and the same
    Retry-After sentinel as load_doab — no parallel crawler.
    """
    from regluit.core.models import Identifier

    active, deleted = set(), set()
    raw_seen = 0
    malformed = []  # Per Codex: catch producer/consumer strictness drift
                    # — see ID_RE validation below.
    try:
        for header in doab.doab_client.listIdentifiers(metadataPrefix='oai_dc'):
            raw_seen += 1
            bare = doab.getdoab(header.identifier())
            if not bare:
                continue
            # Producer strictness must match consumer strictness:
            # load_input_ids() (used both by --ids-file and --use-active-file)
            # validates against ID_RE. Emitting an artifact line that won't
            # round-trip through load_input_ids() is silent waste at best,
            # and a hidden DOAB OAI namespace drift at worst. Refuse rather
            # than emit such records into the universal snapshot.
            if not ID_RE.match(bare):
                if len(malformed) < 10:  # cap memory; first 10 is enough to diagnose
                    malformed.append((header.identifier(), bare))
                continue
            (deleted if header.isDeleted() else active).add(bare)
    except NoRecordsMatchError:
        raise CommandError(
            "DOAB OAI returned no identifiers — refusing to write an empty "
            "worklist. Check the OAI endpoint before retrying."
        )
    except _PyOAIRateLimitedError as e:
        secs = e.retry_after_seconds or DISCOVERY_RATE_LIMIT_FALLBACK_SECS
        deadline = _now_utc() + datetime.timedelta(seconds=secs)
        write_block_deadline(deadline, stderr=stderr)
        raise CommandError(
            f"DOAB OAI rate-limited (429) during discovery; "
            f"Retry-After={secs}s. Shared sentinel set to "
            f"{deadline.isoformat()}. Re-run after the deadline "
            f"(discovery restarts from scratch)."
        )
    except urllib.error.HTTPError as e:
        if e.code != 429:
            raise
        raw = e.headers.get('Retry-After') if e.headers else None
        # Reuse the shared RFC 9110 parser (delta-seconds OR HTTP-date) so
        # discovery and load_doab interpret Retry-After identically.
        secs = doab.parse_retry_after(raw) or DISCOVERY_RATE_LIMIT_FALLBACK_SECS
        deadline = _now_utc() + datetime.timedelta(seconds=secs)
        write_block_deadline(deadline, stderr=stderr)
        raise CommandError(
            f"DOAB OAI rate-limited (429, stock-pyoai path) during "
            f"discovery; Retry-After={secs}s. Shared sentinel set to "
            f"{deadline.isoformat()}. Re-run after the deadline."
        )

    # Namespace-drift guard: if DOAB changes its OAI identifier namespace,
    # doab.getdoab() returns falsy for every header and we'd silently produce
    # a worklist of 0 (and an orphan list of the ENTIRE local DB). Refuse
    # rather than write a misleading "in sync" / mass-orphan result.
    recognized = len(active) + len(deleted)
    if raw_seen > 0 and recognized == 0:
        raise CommandError(
            f"discovery crawled {raw_seen} OAI headers but recognized 0 DOAB "
            f"IDs — doab.getdoab() namespace mismatch? Refusing to write a "
            f"worklist. Inspect a raw ListIdentifiers header before retrying."
        )

    # Producer/consumer strictness drift: discovery and load_input_ids() must
    # agree on what a valid DOAB ID looks like, or the .active snapshot won't
    # round-trip through --use-active-file on a sister host.
    if malformed:
        sample = ', '.join(f'{raw!r}->{bare!r}' for raw, bare in malformed[:3])
        raise CommandError(
            f"discovery saw {len(malformed)}+ DOAB OAI identifier(s) that "
            f"strip-to a value rejected by ID_RE={ID_RE.pattern!r}. First: "
            f"{sample}. Refusing to write a snapshot a sister host couldn't "
            f"consume. (Likely cause: DOAB introduced a new ID shape; "
            f"either ID_RE needs widening or getdoab() needs tightening.)"
        )

    local = set(
        Identifier.objects.filter(type='doab').values_list('value', flat=True)
    )

    backfill = sorted(active - local, key=numeric_suffix)
    stale = sorted(local & deleted, key=numeric_suffix)
    orphan = sorted(local - active - deleted, key=numeric_suffix)

    # Write order matters: each atomic_write_lines() is per-file atomic
    # (tmp+rename) but the group is not. A crash between writes could leave
    # an inconsistent set of files. The `.ids` worklist is the cache marker
    # (`cache_exists` checks for it), so by writing `.ids` LAST we guarantee
    # that whenever `cache_exists` is True, all four sibling artifacts are
    # fresh and mutually consistent.
    #
    # Universal raw-OAI snapshot — reusable across sister hosts via
    # --use-active-file / --use-deleted-file. Sorted by numeric suffix so
    # the snapshot file is byte-stable across runs that see the same OAI
    # state (helpful for `diff` between crawls).
    atomic_write_lines(active_out, sorted(active, key=numeric_suffix))
    atomic_write_lines(deleted_out, sorted(deleted, key=numeric_suffix))
    # Per-host reports
    atomic_write_lines(stale_out, stale)
    atomic_write_lines(orphan_out, orphan)
    # Per-host worklist LAST (acts as the cache_exists marker)
    atomic_write_lines(ids_out, backfill)

    stdout.write(
        f"[discovery] DOAB active={len(active)} deleted={len(deleted)} "
        f"local={len(local)} -> backfill={len(backfill)} "
        f"stale={len(stale)} (DOAB-deleted, still local) "
        f"orphan={len(orphan)} (local, absent from OAI)"
    )
    stdout.write(
        f"[discovery] wrote worklist={ids_out} "
        f"stale_report={stale_out} orphan_report={orphan_out} "
        f"active_snapshot={active_out} deleted_snapshot={deleted_out}"
    )
    return len(backfill)


def discover_via_active_file(active_file, deleted_file, ids_out, stale_out,
                             orphan_out, stdout, stderr, dry_run=False):
    """Cross-host alternative to discover_missing_ids: read a previously-
    emitted .active (and optional .deleted) snapshot from another machine's
    discovery, diff against THIS host's local DB, and write the same 3
    per-host artifacts (worklist, stale, orphan). Makes **zero DOAB calls**.

    Contract: the .active / .deleted snapshots are the universal halves of a
    prior discover_missing_ids() output. The diff against the local DB is
    fast (in-memory set ops + one Identifier query), so this lets the regluit
    fleet pay the ~17-min DOAB OAI crawl once, not once per host.

    If --use-deleted-file is omitted, `deleted` is treated as empty: the
    stale report is empty, and the orphan report becomes (local - active),
    conflating "DOAB-deleted, still local" with "absent from OAI" — still a
    useful diagnostic, just less precise. The backfill worklist itself is
    unaffected.
    """
    from regluit.core.models import Identifier

    active_ids, _, malformed = load_input_ids(active_file)
    if malformed:
        raise CommandError(
            f"--use-active-file has {len(malformed)} malformed line(s); "
            f"first: line {malformed[0][0]}: {malformed[0][1]!r}"
        )
    if not active_ids:
        raise CommandError(
            f"--use-active-file {active_file} parsed to 0 valid DOAB IDs — "
            f"refusing to write an empty worklist."
        )
    active = set(active_ids)

    deleted = set()
    if deleted_file:
        deleted_ids, _, dmalformed = load_input_ids(deleted_file)
        if dmalformed:
            raise CommandError(
                f"--use-deleted-file has {len(dmalformed)} malformed line(s); "
                f"first: line {dmalformed[0][0]}: {dmalformed[0][1]!r}"
            )
        deleted = set(deleted_ids)
        # Per Codex round-2: catch mismatched snapshot pairs early. A well-
        # formed pair has active ∩ deleted = ∅ (DOAB headers are either
        # active or deleted, not both). Overlap suggests the operator paired
        # an .active from one crawl with a .deleted from a different crawl.
        overlap = active & deleted
        if overlap:
            sample = ', '.join(sorted(overlap, key=numeric_suffix)[:3])
            raise CommandError(
                f"--use-active-file and --use-deleted-file overlap in "
                f"{len(overlap)} ID(s) (first: {sample}). Active and deleted "
                f"sets from the same crawl are disjoint by construction; "
                f"this pair appears to come from different crawls."
            )

    local = set(
        Identifier.objects.filter(type='doab').values_list('value', flat=True)
    )

    backfill = sorted(active - local, key=numeric_suffix)
    stale = sorted(local & deleted, key=numeric_suffix)
    orphan = sorted(local - active - deleted, key=numeric_suffix)

    if dry_run:
        # Per Codex round-3: a validation run must not seed a real cache.
        # Report the diff for the operator and return without touching disk.
        stdout.write(
            f"[discovery/reuse,dry-run] active={len(active)} from "
            f"{active_file}; deleted={len(deleted)}"
            f"{' from ' + deleted_file if deleted_file else ' (not provided)'}; "
            f"local={len(local)} -> backfill={len(backfill)} "
            f"stale={len(stale)} orphan={len(orphan)} "
            f"(no files written under --dry-run)"
        )
        return len(backfill)

    # Same write-order discipline as discover_missing_ids: `.ids` is the
    # cache marker, written LAST so its presence implies all siblings are
    # fresh and mutually consistent.
    atomic_write_lines(stale_out, stale)
    atomic_write_lines(orphan_out, orphan)
    atomic_write_lines(ids_out, backfill)

    stdout.write(
        f"[discovery/reuse] active={len(active)} from {active_file}; "
        f"deleted={len(deleted)}"
        f"{' from ' + deleted_file if deleted_file else ' (not provided)'}; "
        f"local={len(local)} -> backfill={len(backfill)} "
        f"stale={len(stale)} orphan={len(orphan)}"
    )
    stdout.write(
        f"[discovery/reuse] wrote worklist={ids_out} "
        f"stale_report={stale_out} orphan_report={orphan_out} "
        f"(no DOAB OAI calls)"
    )
    return len(backfill)


# --- Main command -------------------------------------------------------------

class Command(BaseCommand):
    help = "Slow, resumable backfill for DOAB IDs missing from the local DB."

    def add_arguments(self, parser):
        parser.add_argument('--ids-file', required=False, default=None,
                            help='Path to newline-delimited DOAB IDs (one per '
                                 'line). Optional: if omitted, the worklist is '
                                 'auto-discovered via DOAB OAI ListIdentifiers '
                                 'and cached next to --state-file.')
        parser.add_argument('--state-file', required=True,
                            help='Path to JSON state file (created if missing)')
        parser.add_argument('--rate', type=float, default=3.0,
                            help='Base seconds between requests (default: 3.0)')
        parser.add_argument('--jitter', type=float, default=0.2,
                            help='Fractional jitter on sleep (default: 0.2 = +/-20%%)')
        parser.add_argument('--max-remote-calls', type=int, default=500,
                            help='Cap on DOAB requests per run (default: 500)')
        parser.add_argument('--max-retry-after', type=int, default=300,
                            help='Retry-After (s) above which to checkpoint+exit (default: 300)')
        parser.add_argument('--error-rate-halt', type=float, default=0.05,
                            help='Unknown-error rate above which to halt (default: 0.05)')
        parser.add_argument('--gone-rate-halt', type=float, default=0.30,
                            help='Gone rate above which to halt for review (default: 0.30)')
        parser.add_argument('--order', choices=['newest-first', 'oldest-first', 'as-given'],
                            default='newest-first',
                            help='Processing order (default: newest-first)')
        parser.add_argument('--id-range',
                            help='Optional numeric range filter, e.g. 170000-179999')
        parser.add_argument('--refresh-ids', action='store_true',
                            help='Force re-discovery (OAI crawl) or re-diff '
                                 '(from --use-active-file) even if a cached '
                                 'worklist exists. Requires a fresh '
                                 '--state-file, since the SHA changes.')
        parser.add_argument('--use-active-file', default=None,
                            help='Path to a previously-emitted .active file '
                                 '(raw DOAB OAI active set from a sister '
                                 'host\'s discovery). When provided, skips '
                                 'the DOAB OAI crawl entirely and diffs this '
                                 'snapshot against THIS host\'s local DB. '
                                 'Mutually exclusive with --ids-file.')
        parser.add_argument('--use-deleted-file', default=None,
                            help='Optional companion to --use-active-file: '
                                 'path to the matching .deleted snapshot. '
                                 'Without it, the stale report is empty and '
                                 'the orphan report conflates DOAB-deleted '
                                 'with absent-from-OAI; the backfill '
                                 'worklist itself is unaffected.')
        parser.add_argument('--dry-run', action='store_true',
                            help='Validate inputs + state; do not call DOAB')
        parser.add_argument('--ignore-retry-after', action='store_true',
                            help='Bypass the shared Retry-After sentinel')

    def handle(self, **opt):
        dry = opt['dry_run']

        # Mutual-exclusion guards for the cross-host reuse flags.
        if opt['use_active_file'] and opt['ids_file']:
            raise CommandError(
                "--use-active-file and --ids-file are mutually exclusive: "
                "the former feeds discovery (then diff against local DB); "
                "the latter bypasses discovery with a pre-built worklist."
            )
        if opt['use_deleted_file'] and not opt['use_active_file']:
            raise CommandError(
                "--use-deleted-file is a companion to --use-active-file; "
                "specify both or neither."
            )

        # Shared Retry-After sentinel — gates ALL DOAB traffic, including
        # discovery (not just the per-record loop, which step 6 still guards
        # independently). A dry run makes zero DOAB calls, so it stays allowed
        # even during a ban (operators need to inspect state during bans).
        # --use-active-file also makes zero DOAB calls during the diff phase,
        # but the per-record load loop downstream still hits DOAB and is
        # gated independently by the same sentinel.
        deadline = read_block_deadline()
        now = _now_utc()
        if deadline and now >= deadline:
            # None if cleared; the live deadline if a concurrent writer left a
            # fresh future ban between our read and the clear (must honor it).
            deadline = clear_sentinel()
        ban_active = bool(deadline and not opt['ignore_retry_after'])

        # --- 0. Resolve worklist: explicit --ids-file, cached, reuse, or discover ---
        if not opt['ids_file']:
            (ids_out, stale_out, orphan_out,
             active_out, deleted_out) = derive_cache_paths(opt['state_file'])
            state_exists = load_state(opt['state_file']) is not None
            cache_exists = os.path.exists(ids_out)
            # Prove compatibility with any existing resumable run BEFORE we
            # crawl DOAB or overwrite any artifact.
            if state_exists and opt['refresh_ids']:
                raise CommandError(
                    f"REFUSE: --refresh-ids would overwrite the SHA-pinned "
                    f"worklist, but a state file already exists at "
                    f"{opt['state_file']} and its run could no longer resume. "
                    f"Use a fresh --state-file with --refresh-ids."
                )
            if state_exists and not cache_exists:
                raise CommandError(
                    f"REFUSE: state file {opt['state_file']} exists but its "
                    f"SHA-pinned worklist {ids_out} is missing. A resumed run "
                    f"needs the original worklist — restore {ids_out}, pass "
                    f"the original --ids-file, or start over with a fresh "
                    f"--state-file. (Not crawling DOAB until this is resolved.)"
                )
            # Per Codex review: don't let an existing local cache silently
            # shadow an explicit cross-host reuse snapshot the operator just
            # passed in. Force them to be explicit.
            if opt['use_active_file'] and cache_exists and not opt['refresh_ids']:
                raise CommandError(
                    f"REFUSE: --use-active-file was given but a cached "
                    f"worklist already exists at {ids_out}. The cached "
                    f"worklist would silently win and your snapshot would be "
                    f"ignored. Either pass --refresh-ids with a fresh "
                    f"--state-file to force a re-diff from your snapshot, or "
                    f"drop --use-active-file to deliberately reuse the cache."
                )
            if cache_exists and not opt['refresh_ids']:
                self.stdout.write(
                    f"[backfill] reusing cached worklist {ids_out} "
                    f"(--refresh-ids + a fresh --state-file to rediscover)"
                )
            elif opt['use_active_file']:
                # Cross-host reuse: no DOAB calls during discovery. The
                # shared sentinel doesn't gate this branch (it only gates
                # DOAB traffic; the per-record load loop below remains
                # independently gated by the same sentinel).
                self.stdout.write(
                    f"[backfill] no --ids-file; reusing active snapshot from "
                    f"{opt['use_active_file']} (no DOAB OAI crawl)..."
                )
                missing = discover_via_active_file(
                    opt['use_active_file'], opt['use_deleted_file'],
                    ids_out, stale_out, orphan_out,
                    self.stdout, self.stderr,
                    dry_run=dry,
                )
                if missing == 0:
                    self.stdout.write(
                        "[backfill] reuse-diff found 0 missing IDs — local "
                        "DB is in sync with the supplied active set. "
                        "Nothing to do."
                    )
                    return
                if dry:
                    self.stdout.write(
                        "[backfill] --dry-run with --use-active-file: diff "
                        "complete, no files written, skipping load loop."
                    )
                    return
            elif dry:
                self.stdout.write(
                    "[backfill] --dry-run with no --ids-file and no cached "
                    "worklist: discovery (ListIdentifiers) is skipped under "
                    "--dry-run — it makes no DOAB calls. Nothing to validate."
                )
                return
            elif ban_active:
                self.stdout.write(
                    f"SKIP: DOAB OAI rate-limited until {deadline.isoformat()} "
                    f"(shared sentinel); cannot discover. "
                    f"Use --ignore-retry-after to override."
                )
                sys.exit(EXIT_CHECKPOINT)
            else:
                self.stdout.write(
                    "[backfill] no --ids-file; discovering missing IDs via "
                    "DOAB OAI ListIdentifiers (single-pass, ~125k headers, "
                    "~17 min)..."
                )
                missing = discover_missing_ids(
                    ids_out, stale_out, orphan_out, active_out, deleted_out,
                    self.stdout, self.stderr,
                )
                if missing == 0:
                    self.stdout.write(
                        "[backfill] discovery found 0 missing IDs — local DB "
                        "is in sync with the DOAB active set. Nothing to do."
                    )
                    return
            opt['ids_file'] = ids_out

        # --- 1. Load + validate input -----------------------------------------
        ids, sha256, malformed = load_input_ids(opt['ids_file'])
        if malformed:
            self.stderr.write(
                f"REFUSE: {len(malformed)} malformed line(s) in --ids-file; "
                f"first: line {malformed[0][0]}: {malformed[0][1]!r}"
            )
            raise CommandError("Malformed input file")
        if not ids:
            raise CommandError("No valid IDs in --ids-file")

        # --- 2. Load or initialize state --------------------------------------
        state = load_state(opt['state_file'])
        if state is not None:
            if state.get('ids_file_sha256') != sha256:
                raise CommandError(
                    f"REFUSE: --ids-file SHA256 changed since state was created. "
                    f"State expects {state.get('ids_file_sha256')[:12]}..., "
                    f"file is {sha256[:12]}.... Use a fresh --state-file or "
                    f"restore the original input."
                )
        else:
            state = init_state(opt['ids_file'], len(ids), sha256)

        # --- 3. Apply --id-range filter ---------------------------------------
        if opt['id_range']:
            try:
                lo_str, hi_str = opt['id_range'].split('-')
                lo, hi = int(lo_str), int(hi_str)
            except ValueError:
                raise CommandError(f"--id-range must be N-M (got {opt['id_range']!r})")
            ids = [i for i in ids if lo <= numeric_suffix(i) <= hi]

        # --- 4. Order ---------------------------------------------------------
        if opt['order'] == 'newest-first':
            ids.sort(key=numeric_suffix, reverse=True)
        elif opt['order'] == 'oldest-first':
            ids.sort(key=numeric_suffix)
        # 'as-given' = preserve file order (already deduped by load)

        # --- 5. Filter out already-terminal ----------------------------------
        pending = [i for i in ids
                   if state['ids'].get(i, {}).get('status') not in TERMINAL]

        self.stdout.write(
            f"[backfill] input={len(ids)} pending={len(pending)} "
            f"sha256={sha256[:12]}... order={opt['order']}"
        )

        if opt['dry_run']:
            self._dry_run_report(ids, pending, state, opt)
            return

        # --- 6. Honor shared Retry-After sentinel -----------------------------
        deadline = read_block_deadline()
        now = _now_utc()
        if deadline and now < deadline and not opt['ignore_retry_after']:
            self.stdout.write(
                f"SKIP: DOAB OAI rate-limited until {deadline.isoformat()} "
                f"(shared sentinel). Use --ignore-retry-after to override."
            )
            sys.exit(EXIT_CHECKPOINT)
        if deadline and now >= deadline:
            live = clear_sentinel()
            if live and not opt['ignore_retry_after']:
                self.stdout.write(
                    f"SKIP: DOAB OAI rate-limited until {live.isoformat()} "
                    f"(concurrent writer; shared sentinel)."
                )
                sys.exit(EXIT_CHECKPOINT)

        # --- 7. Per-record loop -----------------------------------------------
        run_started = _now_iso()
        remote_calls = 0
        unknown_errors = 0
        gone_in_run = 0
        processed_in_run = 0
        exit_reason = 'drained'

        try:
            for doab_id in pending:
                # Stop conditions checked at top of loop
                if remote_calls >= opt['max_remote_calls']:
                    exit_reason = 'max_remote_calls'
                    break
                if processed_in_run >= 50 and (
                    unknown_errors / processed_in_run > opt['error_rate_halt']
                ):
                    exit_reason = 'error_rate_halt'
                    break
                if processed_in_run >= 100 and (
                    gone_in_run / processed_in_run > opt['gone_rate_halt']
                ):
                    exit_reason = 'gone_rate_halt'
                    break

                # 7a. Local precheck (no DOAB call, no sleep). Only short-
                # circuit IDs we have NEVER attempted: a bare doab Identifier
                # for an untouched ID means the nightly cron loaded it fully.
                # For an ID we previously attempted (state entry exists, only
                # non-terminal ones survive the step-5 filter), the Identifier
                # may be from our OWN partially-committed write — autocommit
                # (no transaction.atomic, see 7e) means add_by_doab can commit
                # the Identifier before cover/metadata/ISBN follow-up, then
                # crash. Re-run the idempotent loader to heal rather than
                # freezing a partial load as 'present_locally' forever.
                from regluit.core.models import Identifier
                if (doab_id not in state['ids']
                        and Identifier.objects.filter(
                            type='doab', value=doab_id).exists()):
                    mark_terminal(state, doab_id, 'present_locally',
                                  checked_at=_now_iso(),
                                  note='preexisting_untouched')
                    recompute_totals(state)
                    save_state(opt['state_file'], state)
                    processed_in_run += 1
                    continue

                # 7b. Pacing — before remote call
                jittered_sleep(opt['rate'], opt['jitter'])

                # 7c. Remote fetch (DB-free)
                remote_calls += 1
                record = None
                stop_after_this_record = False  # set True on 429-recovered path
                try:
                    record = doab.get_doab_record(doab_id)
                except _PyOAIRateLimitedError as e:
                    exit_reason = self._handle_rate_limit(
                        e, doab_id, state, opt['max_retry_after']
                    )
                    if exit_reason == 'recovered':
                        # Slept the Retry-After, attempt one final fetch, then
                        # exit regardless of outcome — DOAB asked us to slow
                        # down; we honor the wait but don't keep probing.
                        try:
                            record = doab.get_doab_record(doab_id)
                            remote_calls += 1
                            exit_reason = '429_recovered_single_record'
                            stop_after_this_record = True
                        except Exception as e2:
                            # The courtesy retry itself failed. If it is another
                            # rate-limit, DOAB may now want a LONGER wait than
                            # the first Retry-After — extend the shared sentinel
                            # (monotonic) so the next run honors the new ban
                            # instead of re-hitting a still-banned endpoint.
                            self._extend_sentinel_from_exc(e2)
                            mark_retry(state, doab_id,
                                       f'429_after_wait: {type(e2).__name__}')
                            recompute_totals(state)
                            save_state(opt['state_file'], state)
                            exit_reason = '429_after_wait_still_failing'
                            break
                    else:
                        recompute_totals(state)
                        save_state(opt['state_file'], state)
                        break
                except urllib.error.HTTPError as e:
                    if e.code == 429:
                        # Stock-pyoai fallback path. The patched
                        # EbookFoundation/pyoai fork (pinned in
                        # requirements_versioned.pip) raises
                        # _PyOAIRateLimitedError instead, handled above with
                        # the courtesy retry. If we're here, we're running
                        # against an unpatched pyoai — be conservative: write
                        # the shared sentinel and exit cleanly, no retry. The
                        # next run will honor the sentinel.
                        retry_after = e.headers.get('Retry-After') if e.headers else None
                        # RFC 9110 §10.2.3: Retry-After is delta-seconds OR an
                        # HTTP-date. Bare int() collapses a multi-hour date ban
                        # to DEFAULT_RETRY_AFTER_SECS. Reuse the shared parser
                        # so discovery, the fork path, and this stock fallback
                        # all interpret Retry-After identically.
                        secs = doab.parse_retry_after(retry_after) or DEFAULT_RETRY_AFTER_SECS
                        deadline = _now_utc() + datetime.timedelta(seconds=secs)
                        write_block_deadline(deadline, stderr=self.stderr)
                        mark_retry(state, doab_id,
                                   f'HTTPError 429 (stock pyoai fallback); '
                                   f'Retry-After={secs}s')
                        recompute_totals(state)
                        save_state(opt['state_file'], state)
                        exit_reason = 'stock_pyoai_429_fallback'
                        break
                    if 500 <= e.code < 600:
                        mark_retry(state, doab_id, f'HTTPError {e.code}')
                        recompute_totals(state)
                        save_state(opt['state_file'], state)
                        exit_reason = 'transient_failure'
                        break
                    # 4xx other than 429: data-specific, log + halt
                    logger.exception('Unexpected HTTPError %s for %s', e.code, doab_id)
                    mark_terminal(state, doab_id, 'error_review',
                                  last_error=f'HTTPError {e.code}')
                    recompute_totals(state)
                    save_state(opt['state_file'], state)
                    exit_reason = 'unknown_http_error_halt'
                    break
                except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
                    mark_retry(state, doab_id, f'{type(e).__name__}: {e}')
                    recompute_totals(state)
                    save_state(opt['state_file'], state)
                    exit_reason = 'network_failure'
                    break

                # 7d. Categorize fetch result
                if record is None:
                    # IdDoesNotExistError already swallowed by get_doab_record
                    mark_terminal(state, doab_id, 'gone')
                    gone_in_run += 1
                    processed_in_run += 1
                    recompute_totals(state)
                    save_state(opt['state_file'], state)
                    if stop_after_this_record:
                        break
                    continue

                # Detect deleted-or-empty OAI record: header marks it deleted
                # OR has no metadata content. add_by_doab() would return None
                # in both cases, but we'd lose the gone/error_review distinction;
                # categorize as gone here before the loader call.
                if record[0].isDeleted() or not record[1]:
                    mark_terminal(state, doab_id, 'gone',
                                  note='oai_marked_deleted')
                    gone_in_run += 1
                    processed_in_run += 1
                    recompute_totals(state)
                    save_state(opt['state_file'], state)
                    if stop_after_this_record:
                        break
                    continue

                # 7e. Local DB write. Deliberately NOT wrapped in
                # transaction.atomic(): add_by_doab() interleaves DB writes
                # with its own downstream HTTP calls — online_to_download()
                # (timeout up to 60s) and the cover fetch via store_doab_cover()
                # (a redirect chain of requests.get(timeout=(5,60)) calls, up
                # to ~120s). An atomic() wrapper would hold an RDS transaction
                # open across minutes of network I/O per record — undo-log
                # growth and connection-pool pressure against the live site,
                # ~20.6k times. The production nightly cron (load_doab_oai)
                # has called add_by_doab with no transaction wrapper for years;
                # autocommit + add_by_doab's idempotency (a partial-state retry
                # re-heals) is the loader's established safety model. The
                # backfill processes the same records the same way — matching
                # the cron is both safer here and consistent with prod.
                try:
                    edition = doab.add_by_doab(doab_id, record=record)
                except IntegrityError:
                    # Race with nightly cron between precheck (7a) and write
                    from regluit.core.models import Identifier
                    if Identifier.objects.filter(type='doab', value=doab_id).exists():
                        mark_terminal(state, doab_id, 'present_locally',
                                      note='race_resolved')
                        processed_in_run += 1
                        recompute_totals(state)
                        save_state(opt['state_file'], state)
                        if stop_after_this_record:
                            break
                        continue
                    logger.exception('IntegrityError but ID still absent: %s', doab_id)
                    unknown_errors += 1
                    mark_terminal(state, doab_id, 'error_review',
                                  last_error='IntegrityError')
                    recompute_totals(state)
                    save_state(opt['state_file'], state)
                    exit_reason = 'unknown_exception_halt'
                    break
                except (ValueError, TypeError) as e:
                    # Known data-specific validation errors — terminal, flagged for review
                    logger.warning('Validation error loading %s: %s', doab_id, e)
                    mark_terminal(state, doab_id, 'error_review',
                                  last_error=f'{type(e).__name__}: {e}')
                    processed_in_run += 1
                    recompute_totals(state)
                    save_state(opt['state_file'], state)
                    if stop_after_this_record:
                        break
                    continue
                except Exception as e:
                    # Unknown — HALT, do NOT mark terminal
                    logger.exception('Unknown exception loading %s', doab_id)
                    mark_retry(state, doab_id, f'{type(e).__name__}: {e}')
                    unknown_errors += 1
                    recompute_totals(state)
                    save_state(opt['state_file'], state)
                    exit_reason = 'unknown_exception_halt'
                    break

                # 7f. Categorize write result. Active-record fetches that
                # still return None from add_by_doab indicate a real loader
                # anomaly (not the deleted case — that's already handled above).
                if edition is None:
                    mark_terminal(state, doab_id, 'error_review',
                                  last_error='add_by_doab returned None')
                else:
                    mark_terminal(state, doab_id, 'ok',
                                  edition_id=getattr(edition, 'id', None))
                processed_in_run += 1
                recompute_totals(state)
                save_state(opt['state_file'], state)
                if stop_after_this_record:
                    break
        finally:
            state['last_run'] = {
                'started_at': run_started,
                'finished_at': _now_iso(),
                'exit_reason': exit_reason,
                'remote_calls': remote_calls,
                'processed': processed_in_run,
                'unknown_errors': unknown_errors,
                'gone_in_run': gone_in_run,
            }
            recompute_totals(state)
            save_state(opt['state_file'], state)

        terminal_count = sum(state['totals'][s] for s in TERMINAL)
        pct = (100.0 * terminal_count / state['ids_file_count']
               if state['ids_file_count'] else 0)
        self.stdout.write(
            f"[backfill] run done: ok={state['totals']['ok']} "
            f"gone={state['totals']['gone']} "
            f"present_locally={state['totals']['present_locally']} "
            f"retry={state['totals']['retry']} "
            f"error_review={state['totals']['error_review']} "
            f"exit={exit_reason} "
            f"pct_complete={pct:.1f}% "
            f"remote_calls_this_run={remote_calls}"
        )
        # Nonzero exit if we stopped for a reason other than draining
        if exit_reason == 'drained':
            return  # EXIT_OK — worklist fully terminal; runner writes .done
        sys.exit(EXIT_HALT if exit_reason in HALT_REASONS else EXIT_CHECKPOINT)

    # --- helpers -------------------------------------------------------------

    def _extend_sentinel_from_exc(self, exc):
        """Persist a Retry-After carried by exc (fork RateLimitedError or
        stock HTTPError 429). write_block_deadline is monotonic, so this only
        ever lengthens an active ban, never shortens it. Non-rate-limit
        exceptions fall back to DEFAULT_RETRY_AFTER_SECS so a failed courtesy
        retry still imposes a brief cool-off rather than zero."""
        secs = None
        if isinstance(exc, _PyOAIRateLimitedError):
            secs = getattr(exc, 'retry_after_seconds', None)
        elif isinstance(exc, urllib.error.HTTPError) and exc.code == 429:
            raw = exc.headers.get('Retry-After') if exc.headers else None
            secs = doab.parse_retry_after(raw)
        if not secs:
            secs = DEFAULT_RETRY_AFTER_SECS
        write_block_deadline(
            _now_utc() + datetime.timedelta(seconds=secs), stderr=self.stderr
        )

    def _handle_rate_limit(self, exc, doab_id, state, max_retry_after):
        """Apply Retry-After policy. Returns exit_reason or 'recovered'."""
        secs = exc.retry_after_seconds or DEFAULT_RETRY_AFTER_SECS
        # Persist sentinel so other commands honor it too
        deadline = _now_utc() + datetime.timedelta(seconds=secs)
        write_block_deadline(deadline, stderr=self.stderr)
        if secs <= max_retry_after:
            self.stdout.write(
                f"[backfill] 429 on {doab_id}; sleeping {secs}s then single retry"
            )
            time.sleep(secs)
            return 'recovered'  # caller retries once, then exits regardless
        else:
            mark_retry(state, doab_id, f'Retry-After={secs}s exceeds cap={max_retry_after}s')
            self.stdout.write(
                f"[backfill] 429 on {doab_id}; Retry-After={secs}s > cap "
                f"{max_retry_after}s; checkpoint + exit (sentinel set to "
                f"{deadline.isoformat()})"
            )
            return 'retry_after_too_long'

    def _dry_run_report(self, ids, pending, state, opt):
        from regluit.core.models import Identifier
        first10 = pending[:10]
        last10 = pending[-10:]
        present_preview = Identifier.objects.filter(
            type='doab', value__in=pending[:1000]
        ).count()
        terminal_count = sum(state['totals'][s] for s in TERMINAL)
        self.stdout.write("=== DRY RUN ===")
        self.stdout.write(f"  total input IDs:      {len(ids)}")
        self.stdout.write(f"  already terminal:     {terminal_count}")
        self.stdout.write(f"  pending this run:     {len(pending)}")
        self.stdout.write(f"  precheck preview*:    {present_preview} of first 1000 pending already in local DB")
        self.stdout.write(f"  order:                {opt['order']}")
        self.stdout.write(f"  range filter:         {opt['id_range'] or 'none'}")
        self.stdout.write(f"  rate:                 {opt['rate']}s ± {opt['jitter']*100:.0f}%")
        self.stdout.write(f"  max-remote-calls:     {opt['max_remote_calls']}")
        self.stdout.write(f"  max-retry-after:      {opt['max_retry_after']}s")
        self.stdout.write(f"  first 10 to process:  {first10}")
        self.stdout.write(f"  last 10 to process:   {last10}")
        self.stdout.write("  (* preview excludes IDs already terminal in state)")
