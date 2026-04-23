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

    Signature (for dedupe) combines:
      1. Exception type name (e.g. "TemplateDoesNotExist")
      2. Traceback leaf frame (filename, lineno) — the actual user-code
         location that raised, NOT the logging call site
      3. Request path, if the record has a request attribute (Django's
         django.request logger sets this)

    We deliberately do NOT use (record.module, record.funcName,
    record.lineno) as the signature, because for django.request errors
    those identify Django's shared log_response call site — every 500
    from every view would collide on one signature and only the first
    would ever get through the filter. Walking to the traceback leaf
    gives the distinct application frame.

    First occurrence of a signature in the window passes; subsequent
    copies are suppressed.

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

    @staticmethod
    def _signature_from_exc_info(exc_info):
        """Return (exc_type_name, (leaf_file, leaf_lineno)) or (None, None)."""
        if not exc_info or exc_info[0] is None:
            return None, None
        exc_type_name = exc_info[0].__name__
        tb = exc_info[2]
        # Walk to the deepest frame — that's where the exception actually
        # originated, as opposed to where it was caught/logged.
        while tb is not None and tb.tb_next is not None:
            tb = tb.tb_next
        leaf = None
        if tb is not None:
            try:
                leaf = (tb.tb_frame.f_code.co_filename, tb.tb_lineno)
            except Exception:
                leaf = None
        return exc_type_name, leaf

    def filter(self, record):
        exc_type_name, leaf = self._signature_from_exc_info(
            getattr(record, "exc_info", None)
        )

        # If no exception info, fall back to the record's own module/lineno.
        # Most mail_admins records carry exc_info (django.request sets it
        # on 500s), but this keeps the filter well-defined for logger.error
        # calls without exceptions.
        if leaf is None:
            leaf = (
                getattr(record, "module", None),
                getattr(record, "lineno", None),
            )

        # Include request.path if available. django.request attaches the
        # request object to records. Distinct paths hitting the same bug
        # will each get one email per window — slight amplification, but
        # bounded, and preserves the signal "this bug affects multiple
        # URLs" while still cutting bot-hammer floods by orders of
        # magnitude.
        path = None
        request = getattr(record, "request", None)
        if request is not None:
            path = getattr(request, "path", None)

        signature = (exc_type_name, leaf, path)

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
