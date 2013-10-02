from . import backends

def authenticate(user,library):
    backend= getattr(backends, library.backend + '_authenticate')
    return backend(user, library)