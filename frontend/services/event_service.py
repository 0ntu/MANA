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


# fetch the tasks for the current user
def get_tasks(token: str) -> list[dict]:
    url = f"{BACKEND_URL}/tasks"
    resp = requests.get(url, headers=build_auth_headers(token), timeout=20)
    try:
        data = resp.json()
    except Exception:
        data = {"detail": resp.text}

    if resp.status_code >= 400:
        raise RuntimeError(data.get("detail") or "Failed to fetch tasks")
    return data


# mark a task as completed
def finish_task(token: str, task_id: str) -> dict:
    url = f"{BACKEND_URL}/tasks/{task_id}/finish"
    resp = requests.post(url, headers=build_auth_headers(token), timeout=20)
    try:
        data = resp.json()
    except Exception:
        data = {"detail": resp.text}

    if resp.status_code >= 400:
        raise RuntimeError(data.get("detail") or "Failed to finish task")
    return data

