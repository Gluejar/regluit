import requests
from django.conf import settings

mobigen_url = settings.MOBIGEN_URL
mobigen_user_id = settings.MOBIGEN_USER_ID
mobigen_password = settings.MOBIGEN_PASSWORD



def convert_to_mobi(input_url, input_format="application/epub+zip"):
    
    """
    return a string with the output of mobigen computation
    
    """

    # using verify=False since at the moment, using a self-signed SSL cert.

    payload = requests.get(input_url).content 

    headers = {'Content-Type': input_format}
    r = requests.post(mobigen_url, auth=(mobigen_user_id, mobigen_password),
                      data=payload, headers=headers)

    # if HTTP reponse code is ok, the output is the mobi file; else error message
    if r.status_code == 200:
        return r.content
    else:
        raise Exception("{0}: {1}".format(r.status_code, r.content))

