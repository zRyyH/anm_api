from config import SETTINGS
import requests
import logging

logger = logging.getLogger(__name__)


def _post(endpoint: str, json: dict) -> dict:
    r = requests.post(f"{SETTINGS['directus_url']}/{endpoint}", json=json, timeout=15)
    if not r.ok:
        raise RuntimeError(f"{endpoint} falhou ({r.status_code}): {r.text}")
    return r.json()["data"]


def login(email: str, password: str) -> dict:
    return _post("auth/login", {"email": email, "password": password, "mode": "json"})


def refresh(refresh_token: str) -> dict:
    return _post("auth/refresh", {"refresh_token": refresh_token})


def get_me(access_token: str) -> dict:
    r = requests.get(
        f"{SETTINGS['directus_url']}/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=15,
    )
    if r.status_code == 401:
        return {}
    r.raise_for_status()
    return r.json()["data"]
