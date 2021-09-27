from django.conf import settings
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication
from django.utils import timezone

from helpdesk.models import TemporaryTokenModel


class TemporaryTokenAuthentication(TokenAuthentication):
    model = TemporaryTokenModel

    def authenticate_credentials(self, key):
        user, token=super().authenticate_credentials(key=key)
        if(timezone.now()-token.last_active).seconds > settings.TOKEN_TTL:
            token.delete()
            raise exceptions.AuthenticationFailed('Token died')
        else:
            token.last_active=timezone.now()
            token.save()
        return user, token