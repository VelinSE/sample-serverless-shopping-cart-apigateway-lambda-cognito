import os
from base64 import b64encode
from urllib.parse import urlencode
from requests import HTTPError

COGNITO_URL="http://cognito-idp.localhost.localstack.cloud:4566/_aws/cognito-idp/oauth2/token"

class AuthMixin:
    jwt = None

    def get_auth_token(self):
        if self.jwt:
            return self.jwt

        auth_header = b64encode(f"{os.environ['client_id']}:{os.environ['client_secret']}".encode()).decode()
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {auth_header}"
        }

        params = urlencode({
            "grant_type": "client_credentials",
            "client_id": os.environ["client_id"]
        })

        try:            # Note: self.client comes from HttpUser.
            with self.client.post(COGNITO_URL, params=params, headers=headers) as res:
                res.raise_for_status()  # Raises HTTPError for bad responses.
                self.jwt = res.json()["access_token"]
                return self.jwt
        except HTTPError as e:
            print("Authentication failed:", e)
            return None