import logging

from django.http import HttpResponseForbidden

logger = logging.getLogger(__name__)

BAD_ROBOTS = [
    # Officially documented AI training crawlers (authoritative sources from each company):
    # OpenAI: https://platform.openai.com/docs/bots
    u'gptbot',
    u'chatgpt-user',
    u'oai-searchbot',
    # Anthropic: https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web
    u'claudebot',
    # Perplexity: https://docs.perplexity.ai/guides/bots
    u'perplexitybot',
    u'perplexity-user',
    # Amazon: https://developer.amazon.com/amazonbot
    u'amazonbot',
    # Meta: https://developers.facebook.com/docs/sharing/webmasters/crawler
    u'meta-externalagent',
    u'facebookbot',
    # Common Crawl: https://commoncrawl.org/ccbot
    u'ccbot',
    # Diffbot: https://docs.diffbot.com/docs/does-crawl-respect-robotstxt
    u'diffbot',

    # Real crawlers, not formally documented by operator:
    u'bytespider',       # ByteDance/TikTok — widely observed, no official docs page
    u'cohere-ai',        # Cohere — appears in logs, no official crawler docs
    u'timpibot',         # Timpi decentralized search — no formal docs page
    u'imagesiftbot',     # Hive/ImageSift — documented on imagesift.com/about

    # Deprecated Anthropic UA strings (replaced by claudebot, but kept for residual traffic):
    u'anthropic-ai',
    u'claude-web',
]
# Removed (not actual UA strings — robots.txt tokens only, never appear in request headers):
#   google-extended, applebot-extended
# Removed (defunct/inactive operators):
#   omgilibot (replaced by Webzio), memorybot (Internet Memory Foundation, ~2015)


def _sanitize_ua(user_agent):
    """Sanitize user-agent for safe logging (strip control chars, cap length)."""
    clean = ''.join(c for c in user_agent if c >= ' ' and c != '\x7f')
    return clean[:200]


def is_bad_robot(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    if not user_agent:
        # Empty UA is almost never a legitimate browser; block it.
        logger.debug("empty user-agent from %s", request.META.get('REMOTE_ADDR', '?'))
        return True
    try:
        ua_lower = user_agent.lower()
    except UnicodeDecodeError:
        return True
    for robot in BAD_ROBOTS:
        if robot in ua_lower:
            return True
    return False


class BotBlockingMiddleware:
    """Block known AI crawler and bad-bot user agents for all views.

    Runs early in the middleware stack — before session, CSRF, and auth — so
    bot requests are rejected with minimal processing cost.  Individual views
    that need fine-grained control (e.g. download_ebook) may still call
    is_bad_robot() directly, but the middleware handles the common case.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if is_bad_robot(request):
            ua = _sanitize_ua(request.META.get('HTTP_USER_AGENT', ''))
            logger.debug(
                "Bot blocked by middleware: %s from %s",
                ua,
                request.META.get('REMOTE_ADDR', '?'),
            )
            return HttpResponseForbidden("Automated access is not permitted.")
        return self.get_response(request)
