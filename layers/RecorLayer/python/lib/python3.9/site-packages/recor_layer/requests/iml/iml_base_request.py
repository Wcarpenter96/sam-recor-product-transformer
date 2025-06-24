import os


class ImlBaseRequest:
    def __init__(self):
        self.base_url = os.getenv("IML_BASE_URL")
        self.default_params = {"token": os.getenv("IML_AUTH_TOKEN")}
