from datetime import datetime

from django.conf import settings
from django.contrib import auth
from django.utils.deprecation import MiddlewareMixin


class AuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_superuser:
            if request.session.get('last_active'):
                print('last_activ:   ', datetime.fromtimestamp(request.session.get('last_active')))
                print(datetime.timestamp(datetime.now()) - request.session['last_active'])

                if datetime.timestamp(datetime.now()) - request.session['last_active'] > settings.TOKEN_TTL:
                    auth.logout(request)
                else:
                    request.session['last_active'] = datetime.timestamp(datetime.now())
            else:
                request.session['last_active'] = datetime.timestamp(datetime.now())
