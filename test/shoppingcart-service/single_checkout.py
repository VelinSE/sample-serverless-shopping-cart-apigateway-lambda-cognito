from locust import HttpUser, task, between

from shared.auth_mixin import AuthMixin
from shared.get_product_ids import get_product_ids

import random
from requests import HTTPError

class SingleCheckoutUser(HttpUser, AuthMixin):
    wait_time = between(0.2, 1)

    @task
    def order_checkout(self):
        if self.get_auth_token():
            headers = {
                "Authorization": f"Bearer {self.jwt}"
            }
            productId = random.choice(get_product_ids())

            try:
                self.client.post("/cart", headers=headers, json={ "productId": productId })
                self.client.post("/cart/checkout", headers=headers)
            except HTTPError as e:
                print("ERROR", e)
