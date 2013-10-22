from django.contrib.auth.forms import AuthenticationForm

class AuthForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        if request and request.method == 'GET':
            saved_un= request.COOKIES.get('un', None)
            super(AuthForm, self).__init__(initial={"username":saved_un},*args, **kwargs)
        else:
            super(AuthForm, self).__init__(*args, **kwargs)

