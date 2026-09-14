import datetime
import os
import sys
import traceback

from django.core.management.base import BaseCommand

from regluit.core.loaders import doab

# Persisted across cron runs so we honor DOAB's Retry-After instead of
# re-attempting inside the ban window (which extends the ban).
#
# Lives under /var/log/regluit because that directory already exists on prod,
# is writable by the deploy user, and is excluded from the daily log-cleanup
# cron (which targets `*.log` and `*.log.*` only). Override with the
# DOAB_OAI_SENTINEL_PATH environment variable for non-prod environments.
DEFAULT_SENTINEL = '/var/log/regluit/doab-oai-retry-after.state'
SENTINEL_PATH = os.environ.get('DOAB_OAI_SENTINEL_PATH', DEFAULT_SENTINEL)


def timefromiso(datestring):
    try:
        return datetime.datetime.strptime(datestring, "%Y-%m-%d")
    except ValueError:
        return datetime.datetime.strptime(datestring, "%Y-%m-%dT%H:%M:%S")


def _now_utc():
    return datetime.datetime.now(datetime.timezone.utc)


def read_block_deadline(path=SENTINEL_PATH):
    """Return the persisted Retry-After deadline (tz-aware UTC), or None."""
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            raw = f.read().strip()
        if not raw:
            return None
        parsed = datetime.datetime.fromisoformat(raw)
    except (ValueError, OSError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.timezone.utc)
    return parsed


def write_block_deadline(deadline, path=SENTINEL_PATH, stderr=None):
    """Persist the deadline; on failure, write a loud traceback to stderr.

    Silent failures here would mask permission/path bugs and reintroduce the
    ban-extension loop this whole patch exists to prevent.
    """
    # Monotonic: never shorten an active ban. cron and backfill co-own this
    # file; without this, a short 429 racing a long one (or a stale writer)
    # could replace a longer deadline with a shorter one and let us hit a
    # still-banned endpoint early. Only ever move the deadline later.
    existing = read_block_deadline(path)
    if existing is not None and existing >= deadline:
        return True
    try:
        with open(path, 'w') as f:
            f.write(deadline.isoformat())
        return True
    except OSError:
        target = stderr if stderr is not None else sys.stderr
        target.write(
            'WARN: failed to persist DOAB OAI Retry-After sentinel at {}\n'.format(path)
        )
        traceback.print_exc(file=target)
        return False


def clear_sentinel(path=SENTINEL_PATH):
    """Intentionally NEVER deletes the sentinel file.

    An expired deadline is already harmless: every caller compares it to
    `now` and proceeds, and the next 429 overwrites it (write is monotonic).
    Deleting introduces an unavoidable read-then-remove TOCTOU — a fresh
    future deadline written by another process (cron vs backfill) between the
    read and os.remove() would be erased, dropping an active DOAB ban. Not
    deleting eliminates that race entirely; the file is a single tiny value
    that is overwritten, never appended.

    Returns the still-active deadline if one is present (caller must honor
    it); returns None if absent or expired (caller may proceed).
    """
    deadline = read_block_deadline(path)
    if deadline is not None and _now_utc() < deadline:
        return deadline  # still-active ban — caller must honor it
    return None


class Command(BaseCommand):
    help = "load doab books via oai"

    def add_arguments(self, parser):
        parser.add_argument('from_date', nargs='?', type=timefromiso,
                            default=None, help="YYYY-MM-DD to start")
        parser.add_argument('--until', nargs='?', type=timefromiso,
                            default=None, help="YYYY-MM-DD to end")
        parser.add_argument('--max', nargs='?', type=int, default=None, help="max desired records")
        parser.add_argument('--ignore-retry-after', action='store_true',
                            help="bypass the persisted Retry-After block (operator override)")

    def handle(self, from_date, **options):
        until_date = options['until']
        max = options['max']
        ignore = options['ignore_retry_after']

        deadline = read_block_deadline()
        now = _now_utc()
        if deadline and now < deadline and not ignore:
            self.stdout.write(
                'SKIP: DOAB OAI rate-limited until {} (honoring Retry-After). '
                'Use --ignore-retry-after to override.'.format(deadline.isoformat())
            )
            return
        if deadline and now >= deadline:
            live = clear_sentinel()
            if live and not ignore:
                self.stdout.write(
                    'SKIP: DOAB OAI rate-limited until {} (concurrent writer; '
                    'honoring Retry-After).'.format(live.isoformat())
                )
                return

        self.stdout.write('starting at date:{} until:{}, max: {}'.format(
                          from_date, until_date, max))
        records, new_doabs, last_time, error = doab.load_doab_oai(from_date, until_date, limit=max)

        if error is not None:
            new_deadline = _now_utc() + datetime.timedelta(seconds=error.retry_after_seconds)
            wrote = write_block_deadline(new_deadline, stderr=self.stderr)
            self.stdout.write(
                'ERROR: DOAB OAI rate-limited (HTTP 429), '
                'retry-after={}s (raw={!r}). {} blocked until {}'.format(
                    error.retry_after_seconds, error.retry_after_raw,
                    'Persisted sentinel:' if wrote else 'Sentinel write failed;',
                    new_deadline.isoformat(),
                )
            )

        self.stdout.write('loaded {} records ({} new), ending at {}'.format(
            records, new_doabs, last_time))
