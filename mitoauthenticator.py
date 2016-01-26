"""
Custom Authenticator to use MIT OIDC OAuth with JupyterHub.
"""

import json
import os

from tornado.auth import OAuth2Mixin, GoogleOAuth2Mixin
from tornado import gen

from oauthenticator.oauth2 import OAuthLoginHandler, OAuthenticator, OAuthCallbackHandler

class MITMixin(OAuth2Mixin):
    _OAUTH_SETTINGS_KEY = 'oauth2'
    _OAUTH_AUTHORIZE_URL = "https://oidc.mit.edu/authorize"
    _OAUTH_ACCESS_TOKEN_URL = "https://oidc.mit.edu/token"
    _OAUTH_USERINFO_URL = "https://oidc.mit.edu/userinfo"

class MITLoginHandler(OAuthLoginHandler, MITMixin):
    pass

class MITOAuthHandler(OAuthCallbackHandler, MITMixin, GoogleOAuth2Mixin):
    def __init__(self, *args, **kwargs):
        OAuthCallbackHandler.__init__(self, *args, **kwargs)
        self.settings[self._OAUTH_SETTINGS_KEY] = {
            'key': self.authenticator.client_id,
            'secret': self.authenticator.client_secret,
            'scope': ['email']
        }

class MITOAuthenticator(OAuthenticator):
    
    login_service = "MIT OIDC"
    
    client_id_env = 'OAUTH_CLIENT_ID'
    client_secret_env = 'OAUTH_CLIENT_SECRET'
    login_handler = MITLoginHandler
    callback_handler = MITOAuthHandler

    def get_handlers(self, app):
        return [
            (r'/oauth_login', self.login_handler),
            (r'/oauth2_callback', self.callback_handler),
        ]
    
    @gen.coroutine
    def authenticate(self, handler):
        access = yield handler.get_authenticated_user(
            redirect_uri=self.oauth_callback_url,
            code=handler.get_argument("code", False))

        user = yield handler.oauth2_request(
            handler._OAUTH_USERINFO_URL,
            access_token=access["access_token"])

        email = user.get("email", "")
        if not email.endswith("@mit.edu"): return None

        email = email.split("@")[0]
        if len(email) <= 0: return None

        return email
