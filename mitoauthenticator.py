"""
Custom Authenticator to use MIT OIDC OAuth with JupyterHub.
"""

import json
import os
import grp

from traitlets import Unicode

from tornado.auth import OAuth2Mixin, GoogleOAuth2Mixin
from tornado import gen

from jupyterhub.handlers.login import LoginHandler

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

    login_handler = MITLoginHandler
    callback_handler = MITOAuthHandler

    def get_handlers(self, app):
        return [
            (r'/login', LoginHandler),
            (r'/oauth_login', self.login_handler),
            (r'/oauth2_callback', self.callback_handler),
        ]
    
    @gen.coroutine
    def authenticate(self, handler, data=None):
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

        # Use username_map to get remapped names.
        self.log.info("Authenticator username: %s." % email)
        email = self.normalize_username(email)
        self.log.info("Remapped username: %s." % email)

        if not self.check_whitelist(email): return None

        return email

class MITGroupOAuthenticator(MITOAuthenticator):

    required_group = Unicode(config=True,
                             help="""Group that all users must belong to.

                            If not given, any user is allowed.
                            """)

    def check_whitelist(self, username):
        if not self.required_group:
            self.log.warning("Group authenticator selected, but no group given - allowing all users.")
            return True

        try:
            group = grp.getgrnam(self.required_group)
            # Check for entry in /etc/group.
            if username in group.gr_mem:
                self.log.info("Allowing user %s via /etc/group membership checking." % username)
                return True
        except KeyError:
            self.log.warning("The required_group does not exist.  Rejecting all users.")

        return False
