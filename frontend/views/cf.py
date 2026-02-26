import logging
import time

import requests

from django.conf import settings

logger = logging.getLogger(__name__)

site_key = settings.CF_TURNSTILE_SITE_KEY
secret_key = settings.CF_TURNSTILE_SECRET_KEY
cf_url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

# Re-validate with Cloudflare after this many seconds (avoids CAPTCHA on every
# download click in a session while still expiring stale validations).
SESSION_CF_EXPIRY = 3600  # 1 hour


def validate(request):
    token = request.GET.get('cf-turnstile-response', None)

    if not token:
        return False

    # Accept cached validation if it's recent and matches the same token
    cached_token = request.session.get('cf_token')
    cached_at = request.session.get('cf_validated_at', 0)
    if cached_token == token and (time.time() - cached_at) < SESSION_CF_EXPIRY:
        return True

    ip = request.META.get('REMOTE_ADDR', None)
    data = {
        "secret": secret_key,
        "response": token,
        "remoteip": ip,
    }
    try:
        response = requests.post(cf_url, json=data, timeout=5)
        response.raise_for_status()
        result = response.json()
        success = result.get("success", False)
        error_codes = result.get("error-codes", [])

    except requests.exceptions.RequestException as e:
        logger.error(f"Cloudflare Turnstile request failed: {e}")
        return False

    if success:
        request.session['cf_token'] = token
        request.session['cf_validated_at'] = time.time()
        return True

    logger.info(f"Turnstile validation failed: {error_codes}")
    return False
