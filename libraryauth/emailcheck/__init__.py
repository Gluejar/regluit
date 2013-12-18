from .data import blacklist

def is_disposable(email_address):
    email_domain = email_address.lower().rsplit('@')[-1]
    return email_domain in blacklist