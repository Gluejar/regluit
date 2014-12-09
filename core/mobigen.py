"""
Utility for calling mobigen

"""

import requests


def convert_to_mobi(input_url, input_format="application/epub+zip"):
    
    """
    return a string with the output of mobigen computation
    
    """


    # substitute file_path with a local epub or html file
    #file_path = "/Users/raymondyee/D/Document/Gluejar/Gluejar.github/regluit/test-data/pg2701.epub"
    #file_type = "application/epub+zip"  

    # where to write the output 
    #output_path = "/Users/raymondyee/Downloads/pg2701.mobi"

    # url of the mobigen service
    mobigen_url = "https://docker.gluejar.com:5001/mobigen"
    mobigen_user_id = "admin"
    mobigen_password = "CXq5FSEQFgXtP_s"

    # read the file and do a http post
    # equivalent curl
    # curl -k --user "admin:CXq5FSEQFgXtP_s" -X POST -H "Content-Type: application/epub+zip" --data-binary "@/Users/raymondyee/D/Document/Gluejar/Gluejar.github/regluit/test-data/pg2701.epub" https://docker.gluejar.com/mobigen:5001 > pg2701.mobi

    # using verify=False since at the moment, using a self-signed SSL cert.

    payload = requests.get(input_url, verify=False).content 

    headers = {'Content-Type': input_format}
    r = requests.post(mobigen_url, auth=(mobigen_user_id, mobigen_password),
                      data=payload, verify=False, headers=headers)

    # if HTTP reponse code is ok, the output is the mobi file; else error message
    if r.status_code == 200:
        return r.content
    else:
        raise Exception("{0}: {1}".format(r.status_code, r.content))
