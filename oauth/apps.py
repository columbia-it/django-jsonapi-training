import logging
import requests

from django.apps import AppConfig
from django.conf import settings

class OauthConfig(AppConfig):
    name = 'oauth'
    log = logging.getLogger(name)

    def ready(self):
        """
        connect to settings.OAUTH2_SERVER's well-known URL to fill out settings.OAUTH2_CONFIG.
        """
        if hasattr(settings, 'OAUTH2_SERVER') and hasattr(settings, 'OAUTH2_CONFIG'):
            url = settings.OAUTH2_SERVER + '/.well-known/openid-configuration'
            try:
                result = requests.get(url)
                if result.status_code == 200:
                    settings.OAUTH2_CONFIG = result.json()
                    settings.OAUTH2_PROVIDER['SCOPES']: {
                        k: '{} scope'.format(k) for k in settings.OAUTH2_CONFIG['scopes_supported']
                    }
                    self.log.debug('succesfully initialized OAUTH2_CONFIG for {}'.format(settings.OAUTH2_SERVER))
                else:
                    self.log.error('failed to get {}'.format(url))
            except requests.exceptions.RequestException as e:
                self.log.error(e)
