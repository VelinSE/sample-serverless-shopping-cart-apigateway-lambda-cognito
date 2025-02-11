from locust import HttpUser, task, between
from os import environ
from base64 import b64encode
from urllib.parse import urlencode
from urllib.error import HTTPError

COGNITO_URL="http://cognito-idp.localhost.localstack.cloud:4566/_aws/cognito-idp/oauth2/token"

class ListCartUser(HttpUser):
    wait_time = between(0.2, 1)
    jwt = None

    def __auth(self):
        if self.jwt:
            return self.jwt
        
        auth_header = b64encode(f"{environ['client_id']}:{environ['client_secret']}".encode()).decode()
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {auth_header}"
        }

        params = urlencode({
            "grant_type": "client_credentials",
            "client_id": environ["client_id"]
        })

        try:
            print("Logging in")
            with self.client.post(COGNITO_URL, params=params, headers=headers) as res:
                self.jwt = res.json()["access_token"]

                return self.jwt
        except HTTPError as e:
            print(e)
        finally:
            return False


    @task
    def list_cart(self):
        if self.__auth():
            headers = {
                "Authorization": f"Bearer {self.jwt}"
            }
            print(headers)
            self.client.post("/cart/migrate", headers=headers)