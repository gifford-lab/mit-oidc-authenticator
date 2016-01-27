# mit-oidc-oauthenticator

Authenticate Jupyter users with MIT OIDC OAuth (MIT's OAuth2/OpenID
service).

This is based on [Google
OAuthenticator](https://github.com/ryanlovett/jh-google-oauthenticator),
which is based on [Github
OAuthenticator](https://github.com/jupyter/oauthenticator).

The class will redirect the user to the [MIT
OIDC](https://oidc.mit.edu/) server, where they can log in with a
Kerberos password, ticket, or client certificates.  The class verifies
a `mit.edu` email suffix, strips it, and returns the bare username as
the Jupyterhub client name.

## Installation

First, install dependencies:

    pip install -r requirements.txt

Then, install the package:

    python setup.py install

## Setup

You will need to create an [OAuth 2.0 client
ID](https://oidc.mit.edu/manage/dev/dynreg)
in the MIT OIDC website. A client secret will be
automatically generated for you. Set the callback URL to:

    http[s]://[your-host]/hub/oauth2_callback

where `[your-host]` is your server's hostname,
e.g. `example.com:8000`.

Then, add the following to your `jupyterhub_config.py` file:

    c.JupyterHub.authenticator_class = 'oauthenticator.MITOAuthenticator'

You will need to provide the callback URL and the MIT OIDC OAuth
client ID and client secret to JupyterHub. For example, if these
values are in the environment variables `$OAUTH_CALLBACK_URL`,
`$OAUTH_CLIENT_ID` and `$OAUTH_CLIENT_SECRET`, you should add the
following to your `jupyterhub_config.py`:

    c.MITOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']
    c.MITOAuthenticator.client_id = os.environ['OAUTH_CLIENT_ID']
    c.MITOAuthenticator.client_secret = os.environ['OAUTH_CLIENT_SECRET']

## Restricting access to a specific group

You can also use the the `MITGroupOAuthenticator` class to restrict
access to a single group (via `/etc/group` membership).  Add the
following lines to your configuration:

    c.JupyterHub.authenticator_class = 'oauthenticator.MITGroupOAuthenticator'
    c.MITGroupOAuthenticator.required_group = [your required group]

If you omit the `required_group` in your configuration, the class will
behave like `MITOAuthenticator` and allow all users.  If you give it
an invalid group, or try to log in as a user not in that group, the
user will be rejected with a HTTP 403 error.
