from locust import HttpUser, task, between
from shared.auth_mixin import AuthMixin

class ListCartUser(HttpUser, AuthMixin):
    wait_time = between(0.2, 1)

    @task
    def list_cart(self):
        if self.get_auth_token():
            headers = {
                "Authorization": f"Bearer {self.jwt}"
            }
            self.client.post("/cart/migrate", headers=headers)