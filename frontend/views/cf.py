import logging

import requests

from django.conf import settings

logger = logging.getLogger(__name__)

site_key = settings.CF_TURNSTILE_SITE_KEY
secret_key = settings.CF_TURNSTILE_SECRET_KEY
cf_url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def validate(request):
    token = request.GET.get('cf-turnstile-response', None)

    if not token:
        return False

    if request.session.get('token') and request.session.get('token') == token:
        return True

    ip = request.META.get('REMOTE_ADDR', None)
    data = {
        "secret": secret_key,
        "response": token,
        "remoteip": ip,
    }
    try:
        response = requests.post(cf_url, json=data)
        response.raise_for_status()
        print( response.json())
        success = response.json().get("success", None)
        error_codes = response.json().get("error_codes", [])
        
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred: {e}")
        return False
    
    if success:
        request.session['token'] = token
        return True

    logger.info(f"validation failed due to: {error_codes}")
    return False
