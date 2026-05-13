"""
doab_utils.py

"""
import datetime
import email.utils
import logging
import os
import re
import sys
import threading
import traceback
from ssl import SSLError
from urllib.parse import urljoin

import requests

from oaipmh.metadata import MetadataReader

from django.conf import settings

from regluit.core import models
from regluit.utils.lang import lang_to_language_code
from .soup import get_soup


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# DOAB rate-limit helpers
#
# Two endpoints on directory.doabooks.org get rate-limited together:
#   - OAI-PMH (used by load_doab_oai in doab.py)
#   - REST/bitstream (used by get_streamdata here and the cover download in
#     doab.py's store_doab_cover)
#
# The OAI path uses a cross-cron sentinel (see core/management/commands/
# load_doab.py). The bitstream path is called per-record inside the OAI
# harvest loop, so it uses an in-process circuit breaker that also persists
# a sentinel — once tripped, all bitstream calls (in this process or the
# next cron run) return None until the deadline passes.
# ---------------------------------------------------------------------------

_BITSTREAM_FALLBACK_SECONDS = 3600  # 1 hour if Retry-After is missing/unparseable
_DEFAULT_BITSTREAM_SENTINEL = '/var/log/regluit/doab-bitstream-retry-after.state'
BITSTREAM_SENTINEL_PATH = os.environ.get(
    'DOAB_BITSTREAM_SENTINEL_PATH', _DEFAULT_BITSTREAM_SENTINEL,
)

_bitstream_lock = threading.Lock()
_bitstream_breaker_until = None  # tz-aware UTC datetime, or None
_bitstream_breaker_loaded = False  # have we read the sentinel file yet?


def parse_retry_after(raw):
    """Parse a Retry-After header value per RFC 9110 §10.2.3.

    Returns an int number of seconds (>= 0), or None if the value is missing
    or cannot be parsed. Accepts both delta-seconds and HTTP-date forms.
    """
    if not raw:
        return None
    raw = raw.strip()
    try:
        seconds = int(raw)
        return max(0, seconds)
    except ValueError:
        pass
    try:
        target = email.utils.parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        return None
    if target is None:
        return None
    if target.tzinfo is None:
        target = target.replace(tzinfo=datetime.timezone.utc)
    now = datetime.datetime.now(datetime.timezone.utc)
    return max(0, int((target - now).total_seconds()))


def _now_utc():
    return datetime.datetime.now(datetime.timezone.utc)


def _read_bitstream_sentinel(path=None):
    path = path or BITSTREAM_SENTINEL_PATH
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


def _write_bitstream_sentinel(deadline, path=None):
    path = path or BITSTREAM_SENTINEL_PATH
    try:
        with open(path, 'w') as f:
            f.write(deadline.isoformat())
        return True
    except OSError:
        sys.stderr.write(
            'WARN: failed to persist DOAB bitstream Retry-After sentinel at {}\n'.format(path)
        )
        traceback.print_exc(file=sys.stderr)
        return False


def _clear_bitstream_sentinel(path=None):
    path = path or BITSTREAM_SENTINEL_PATH
    try:
        os.remove(path)
    except OSError:
        pass


def bitstream_breaker_open():
    """True when the DOAB bitstream circuit breaker is tripped.

    On first call in a process, reads the persisted sentinel so a fresh cron
    run honors the deadline set by a previous run. Logs once when a fresh
    process loads an already-open sentinel, so operators see "this cron ran
    but skipped all cover work due to a persisted ban window."
    """
    global _bitstream_breaker_until, _bitstream_breaker_loaded
    log_loaded = None  # (deadline,) when we should emit the once-per-process load log
    with _bitstream_lock:
        if not _bitstream_breaker_loaded:
            _bitstream_breaker_until = _read_bitstream_sentinel()
            _bitstream_breaker_loaded = True
            if _bitstream_breaker_until and _now_utc() < _bitstream_breaker_until:
                log_loaded = (_bitstream_breaker_until,)
        if _bitstream_breaker_until is None:
            is_open = False
        elif _now_utc() < _bitstream_breaker_until:
            is_open = True
        else:
            # deadline passed — clear in-memory and on-disk
            _bitstream_breaker_until = None
            _clear_bitstream_sentinel()
            is_open = False
    if log_loaded is not None:
        logger.info(
            'DOAB bitstream circuit breaker loaded from sentinel; open until '
            '%s. Cover lookups will be skipped until then.',
            log_loaded[0].isoformat(),
        )
    return is_open


def bitstream_breaker_trip(retry_after_raw, source):
    """Open the circuit breaker. Called when a bitstream endpoint returns 429.

    `source` is a short human label (e.g. "get_streamdata(20.500.12854/176298)")
    used in the single per-trip log line so operators can see which endpoint
    tripped the breaker.
    """
    global _bitstream_breaker_until, _bitstream_breaker_loaded
    seconds = parse_retry_after(retry_after_raw)
    if seconds is None:
        seconds = _BITSTREAM_FALLBACK_SECONDS
    deadline = _now_utc() + datetime.timedelta(seconds=seconds)
    # Hold the lock across the disk write so two threads can't write out of
    # order and leave the shorter deadline persisted. (Two *processes* can
    # still race here, but that's tolerable — cron's only writer in practice
    # is a single load_doab run; the cross-process loss case shortens a ban
    # by at most one Retry-After delta, which is acceptable.)
    with _bitstream_lock:
        if _bitstream_breaker_until and _bitstream_breaker_until > deadline:
            return _bitstream_breaker_until
        _bitstream_breaker_until = deadline
        _bitstream_breaker_loaded = True
        _write_bitstream_sentinel(deadline)
    logger.error(
        'DOAB bitstream API rate-limited (HTTP 429) from %s; circuit breaker '
        'open until %s (retry-after raw=%r, parsed=%ss). Suppressing further '
        'per-record 429 logs.',
        source, deadline.isoformat(), retry_after_raw, seconds,
    )
    return deadline


def _bitstream_breaker_reset_for_tests():
    """Test-only hook: reset module state."""
    global _bitstream_breaker_until, _bitstream_breaker_loaded
    with _bitstream_lock:
        _bitstream_breaker_until = None
        _bitstream_breaker_loaded = False

def doab_lang_to_iso_639_1(lang):
    lang = lang_to_language_code(lang)
    return lang if lang else 'xx'


doab_reader = MetadataReader(
    fields={
        'title': ('textList', 'oai_dc:dc/dc:title/text()'),
        'creator': ('textList', 'oai_dc:dc/dc:creator/text()'),
        'subject': ('textList', 'oai_dc:dc/dc:subject/text()'),
        'description': ('textList', 'oai_dc:dc/dc:description/text()'),
        'publisher': ('textList', 'oai_dc:dc/dc:publisher/text()'),
        'editor': ('textList', 'oai_dc:dc/dc:contributor[@type="Editor"]/text()'),
        'date': ('textList', 'oai_dc:dc/dc:date[@type="Issued"]/text()'),
        'type': ('textList', 'oai_dc:dc/oaire:resourceType/text()'),
        'format': ('textList', 'oai_dc:dc/dc:format/text()'),
        'identifier': ('textList', 'oai_dc:dc/dc:identifier/text()'),
        'source': ('textList', 'oai_dc:dc/dc:source/text()'),
        'language': ('textList', 'oai_dc:dc/dc:language/text()'),
        'relation': ('textList', 'oai_dc:dc/dc:relation/text()'),
        'coverage': ('textList', 'oai_dc:dc/dc:coverage/text()'),
        'rights': ('textList', 'oai_dc:dc/oaire:licenseCondition/@uri'),
        'isbn': ('textList', 'oai_dc:dc/dc:alternateIdentifier[@type="ISBN"]/text()'),
        'doi': ('textList', 'oai_dc:dc/dc:alternateIdentifier[@type="DOI"]/text()'),
    },
    namespaces={
        'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
        'dc' : 'http://purl.org/dc/elements/1.1/',
        'grantor': 'http://purl.org/dc/elements/1.1/',
        'publisher': 'http://purl.org/dc/elements/1.1/',
        'oapen': 'http://purl.org/dc/elements/1.1/',
        'oaire': 'https://raw.githubusercontent.com/rcic/openaire4/master/schemas/4.0/oaire.xsd',
        'datacite': 'https://schema.datacite.org/meta/kernel-4.1/metadata.xsd',
        'doc': 'http://www.lyncode.com/xoai'
    }
)
STOREPROVIDERS = [
    '7switch.com',
    'amazon.ca',
    'amazon.co.uk',
    'amazon.com',
    'amazon.de',
    'amzn.to',
    'apress.com',
    'bloomsbury.com',
    'bod.de',
    'booksdirect.co.za',
    'cabi.org',
    'cdcshoppingcart.uchicago.edu',
    'checkout.sas.ac.uk',
    'duncker-humblot.de',
    'dykinson.com',
    'e-elgar.com',
    'edicions.ub.edu',
    'epubli.de',
    'eurekaselect.com',
    'fondazionecafoscari.storeden.com',
    'global.oup.com',
    'iospress.nl',
    'karolinum.cz',
    'librumstore.com',
    'logos-verlag.de',
    'manchesteruniversitypress.co.uk',
    'mitpress.mit.edu',
    'munishop.muni.cz',
    'nai010.com',
    'nomos-shop.de',
    'palgrave.com',
    'placedeslibraires.fr',
    'play.google.com',
    'press.umich.edu',
    'pressesuniversitairesdeliege.be',
    'publicacions.ub.edu',
    'publicacions.urv.cat',
    'schueren-verlag.de',
    'sci.fo',
    'store.printservice.nl',
    'una-editions.fr',
    'universitaetsverlag.uni-kiel.de',
    'universitetsforlaget.no',
    'urldefense.com',
    'usu.edu',
    'uwapress.uw.edu',
    'wbg-wissenverbindet.de',
    'zalozba.zrc-sazu.si',
]

def online_to_download(url):
    urls = []
    if not url:
        return urls

    elif url.find(u'edp-open.org/books-in-') >= 0:
        # pages needing multi-scrape
        return urls
    else:
        urls.append(url)
    if not urls:
        logging.warning('no valid download urls for %s', url)
    return urls


STREAM_QUERY = 'https://directory.doabooks.org/rest/search?query=handle:{}&expand=bitstreams'

def get_streamdata(handle):
    if bitstream_breaker_open():
        return None
    url = STREAM_QUERY.format(handle)
    try:
        response = requests.get(url, headers={"User-Agent": settings.USER_AGENT}, timeout=(5, 60))
        if response.status_code == 429:
            bitstream_breaker_trip(
                response.headers.get('Retry-After'),
                'get_streamdata({})'.format(handle),
            )
            return None
        items = response.json()
        if items:
            for stream in items[0]['bitstreams']:
                if stream['bundleName'] == "THUMBNAIL":
                    stream['handle'] = handle
                    return stream
        else:
            logger.error("No items in streamdata for %s", handle)
    except requests.exceptions.RequestException as e:
        logger.error(e)
    except SSLError as e:
        logger.error(e)
    except ValueError as e:
        # decoder error
        logger.error(e)

COVER_FSTRING = "https://directory.doabooks.org/bitstream/handle/{handle}/{name}?sequence={sequenceId}&isAllowed=y"
def doab_cover(doab_id):
    stream_data = get_streamdata(doab_id)
    if not stream_data:
        logger.error('get_streamdata failed for %s', doab_id)
        return None
    if 'retrieveLink' in stream_data:
        return f"https://directory.doabooks.org{stream_data['retrieveLink']}"
    return COVER_FSTRING.format(**stream_data)

