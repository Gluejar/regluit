import logging
import logging.handlers
import os
import threading
import time

#https://stackoverflow.com/questions/28054864/use-fileconfig-to-configure-custom-handlers-in-python
logging.handlers = logging.handlers

#https://stackoverflow.com/questions/1407474/does-python-logging-handlers-rotatingfilehandler-allow-creation-of-a-group-writa
class GroupWriteRotatingFileHandler(logging.handlers.RotatingFileHandler):
    def _open(self):
        prevumask = os.umask(0o002)
        #os.fdopen(os.open('/path/to/file', os.O_WRONLY, 0600))
        rtv = logging.handlers.RotatingFileHandler._open(self)
        os.umask(prevumask)
        return rtv

# for django, need to do this in settings
#logging.handlers.GroupWriteRotatingFileHandler = GroupWriteRotatingFileHandler


class RateLimitFilter(logging.Filter):
    """Dedupe log records by signature within a time window.

    Added in response to the 2026-04-23 AdminEmailHandler flood incident
    (7,700+ error emails from a single broken view + bot traffic). See
    EbookFoundation/security-private#11.

    Usage in Django LOGGING config:

        'filters': {
            'mail_admins_rate_limit': {
                '()': 'regluit.utils.custom_logging.RateLimitFilter',
                'rate_seconds': 60,
            },
        },
        'handlers': {
            'mail_admins': {
                'filters': ['require_debug_false', 'mail_admins_rate_limit'],
                ...
            },
        },

    The signature is derived from (module, funcName, lineno, exc_type) —
    so the same exception type from the same location is considered a
    duplicate. First occurrence in the window passes; subsequent copies
    are suppressed.

    State is per-process. With multiple mod_wsgi workers, each holds its
    own rate-limit state, so the effective rate is (n_workers × 1/window).
    That's an ~80% solution: it prevents single-request cascades and
    eliminates bot-hammer floods of identical errors, but doesn't
    strictly bound rate across the whole deployment. Cross-worker
    coordination would require Redis or similar — deferred.
    """

    def __init__(self, name="", rate_seconds=60):
        super().__init__(name)
        self.rate_seconds = rate_seconds
        self._lock = threading.Lock()
        self._last_sent = {}

    def filter(self, record):
        # Key on location + exception type so distinct errors are not
        # conflated but repeated instances of the same error are.
        exc_type_name = None
        if record.exc_info and record.exc_info[0] is not None:
            exc_type_name = record.exc_info[0].__name__
        signature = (
            getattr(record, "module", None),
            getattr(record, "funcName", None),
            getattr(record, "lineno", None),
            exc_type_name,
        )

        now = time.monotonic()
        with self._lock:
            last = self._last_sent.get(signature, 0.0)
            if (now - last) >= self.rate_seconds:
                self._last_sent[signature] = now
                # Opportunistic cleanup so the dict doesn't grow forever
                # in the face of unbounded distinct error signatures.
                if len(self._last_sent) > 1024:
                    cutoff = now - (self.rate_seconds * 10)
                    self._last_sent = {
                        k: v for k, v in self._last_sent.items() if v > cutoff
                    }
                return True
            return False
