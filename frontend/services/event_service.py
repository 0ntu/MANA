import requests

from services.auth_service import BACKEND_URL, build_auth_headers


def add_event(token: str, payload: dict) -> dict:
    """
    Creates a scheduled task/event via backend POST `/tasks/create`.
    Payload is expected to align with backend's CreateTask model.
    """
    url = f"{BACKEND_URL}/tasks/create"
    resp = requests.post(url, json=payload, headers=build_auth_headers(token), timeout=20)
    try:
        data = resp.json()
    except Exception:
        data = {"detail": resp.text}

    if resp.status_code >= 400:
        raise RuntimeError(data.get("detail") or "Failed to add event")
    return data

