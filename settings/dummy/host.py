# host.py
# copy this file to settings/keys/ and replace the dummy values with real ones
# or generate it from the ansible vault
import os

# you can use this to generate a key: http://www.miniwebtool.com/django-secret-key-generator/
SECRET_KEY = os.environ.get("SECRET_KEY", '01234567890123456789012345678901234567890123456789')

# you'll need to register a GoogleBooks API key
# https://code.google.com/apis/console
GOOGLE_BOOKS_API_KEY = os.environ.get("GOOGLE_BOOKS_API_KEY", "012345678901234567890123456789012345678")


# Amazon SES
# create with https://console.aws.amazon.com/ses/home?region=us-east-1#smtp-settings:
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", '01234567890123456789')
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD",  '01234567890123456789012345678901234567890123')

# support@icontact.nl
BOOXTREAM_API_KEY = os.environ.get("BOOXTREAM_API_KEY", None) # 30 chars
BOOXTREAM_API_USER = os.environ.get("BOOXTREAM_API_USER", 'user')

# https://console.developers.google.com/apis/credentials/oauthclient/
# unglue.it (prod) SOCIAL_AUTH_GOOGLE_OAUTH2_KEY #2
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get("_KEY", '012345678901-01234567890123456789012345678901.apps.googleusercontent.com')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get("_SECRET", '012345678901234567890123')

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", '01234567890123456789')
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", '') # 40 chars

DATABASE_USER = os.environ.get("DATABASE_USER", 'root')
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD", '')
DATABASE_HOST = os.environ.get("DATABASE_HOST", '')
