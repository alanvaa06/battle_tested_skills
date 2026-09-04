import os

import requests

BASE = "https://api.example.com/v1"


def fetch() -> str:
    token = os.environ["API_KEY"]
    return requests.get(BASE, headers={"Authorization": token}).text
