from locust import HttpUser, task, between

from shared.auth_mixin import AuthMixin
from shared.get_product_ids import get_product_ids

import random

class AuthenticatedUser(HttpUser, AuthMixin):
    wait_time = between(0.2, 1)
    headers = None

    def on_start(self):
        jwt = self.get_auth_token()
        self.headers = {
            "Authorization": f"Bearer {jwt}"
        }

    @task(4)
    def order_single(self):
        try:
            productId = random.choice(get_product_ids())

            self.client.post("/cart", headers=self.headers, json={ "productId": productId })
            self.client.post("/cart/checkout", headers=self.headers)
        except Exception as e:
            print("ERROR", e)

    @task(1)
    def order_multiple(self):
        try:
            first_product = random.choice(get_product_ids())
            second_product = random.choice(get_product_ids())

            self.client.post("/cart", headers=self.headers, json={ "productId": first_product })
            self.client.post("/cart", headers=self.headers, json={ "productId": second_product })

            self.client.get("/cart", headers=self.headers)

            self.client.post("/cart/checkout", headers=self.headers)
        except Exception as e:
            print("ERROR", e)

    @task(2)
    def order_single_update_qty(self):
        try:
            productId = random.choice(get_product_ids())

            self.client.post("/cart", headers=self.headers, json={ "productId": productId })
            self.client.get("/cart", headers=self.headers)
            self.client.put(
                f"/cart/{productId}",
                headers=self.headers,
                json={ "productId": productId, "quantity": 4 }
            )

            self.client.post("/cart/checkout", headers=self.headers)
        except Exception as e:
            print("ERROR", e)