from locust import HttpUser, task, between

class ListCartUser(HttpUser):
    wait_time = between(0.2, 1)
    
    @task
    def list_cart(self):
        self.client.get("/cart")