import os
from typing import Any, Optional, Tuple

import requests


BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _extract_token_and_user(payload: dict[str, Any]) -> Tuple[Optional[str], Optional[dict[str, Any]]]:
    token = payload.get("access_token") or payload.get("jwt_token") or payload.get("token")
    user = payload.get("user") or payload.get("current_user")
    return token, user


def signup(username: str, password: str) -> tuple[str, dict[str, Any]]:
    """
    Calls backend POST `/authentication/signup`.
    Returns `(token, user)`.
    """
    url = f"{BACKEND_URL}/authentication/signup"
    resp = requests.post(url, json={"username": username, "password": password}, timeout=20)
    try:
        data = resp.json()
    except Exception:
        data = {"detail": resp.text}

    if resp.status_code >= 400:
        raise RuntimeError(data.get("detail") or "Signup failed")

    token, user = _extract_token_and_user(data)
    if not token:
        raise RuntimeError("Signup succeeded but no token was returned by backend")
    return token, user or {}


def login(username: str, password: str) -> tuple[str, dict[str, Any]]:
    """
    Calls backend POST `/authentication/login`.
    Returns `(token, user)`.
    """
    url = f"{BACKEND_URL}/authentication/login"
    resp = requests.post(url, json={"username": username, "password": password}, timeout=20)
    try:
        data = resp.json()
    except Exception:
        data = {"detail": resp.text}

    if resp.status_code >= 400:
        raise RuntimeError(data.get("detail") or "Login failed")

    token, user = _extract_token_and_user(data)
    if not token:
        raise RuntimeError("Login succeeded but no token was returned by backend")
    return token, user or {}


def get_backend_url() -> str:
    return BACKEND_URL


def build_auth_headers(token: str) -> dict[str, str]:
    return _auth_headers(token)
