import os
from typing import Any, Optional

import requests


BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def get_share_status(token: str) -> Optional[str]:
    # GET `/share/status`.
    # returns the share_token if enabled
    url = f"{BACKEND_URL}/share/status"
    resp = requests.get(url, headers=_auth_headers(token), timeout=20)
    if resp.status_code >= 400:
        return None
    data = resp.json()
    return data.get("share_token")


def generate_share_link(token: str) -> str:
    # POST `/share/generate`.
    # returns the new share_token.
    url = f"{BACKEND_URL}/share/generate"
    resp = requests.post(url, headers=_auth_headers(token), timeout=20)
    if resp.status_code >= 400:
        raise RuntimeError("Failed to generate share link")
    data = resp.json()
    return data["share_token"]


def disable_share_link(token: str) -> None:
    # DELETE `/share/disable`.
    url = f"{BACKEND_URL}/share/disable"
    resp = requests.delete(url, headers=_auth_headers(token), timeout=20)
    if resp.status_code >= 400:
        raise RuntimeError("Failed to disable share link")


def get_public_schedule(share_token: str) -> Optional[dict[str, Any]]:
    # GET `/public/schedule/{share_token}`.
    # returns schedule data
    url = f"{BACKEND_URL}/public/schedule/{share_token}"
    resp = requests.get(url, timeout=20)
    if resp.status_code == 404:
        return None
    if resp.status_code >= 400:
        return None
    return resp.json()
