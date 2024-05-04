import logging

from bs4 import BeautifulSoup
import requests

from django.conf import settings

logger = logging.getLogger(__name__)

def get_soup(url, user_agent=settings.USER_AGENT, follow_redirects=False, verify=True):
    try:
        response = requests.get(url, headers={"User-Agent": user_agent},
                                allow_redirects=follow_redirects, verify=verify)
    except requests.exceptions.MissingSchema:
        response = requests.get('http://%s' % url, headers={"User-Agent": user_agent})
    except requests.exceptions.ConnectionError as e:
        logger.error("Connection refused for %s", url)
        logger.error(e)
        return None
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'lxml')

        # make sure document has a base
        if not soup.find('base'):
            obj = soup.find('head')
            if obj:
                obj.append(soup.new_tag("base", href=response.url))
            else:
                logger.error('No head for  %s', url)
        return soup
    else:
        logger.error('%s returned code %s', url, response.status_code)
    return None
