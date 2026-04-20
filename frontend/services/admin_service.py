import requests

from services.auth_service import BACKEND_URL, build_auth_headers


def get_all_users(token: str) -> list[dict]:
    resp = requests.get(
        f"{BACKEND_URL}/admin/users",
        headers=build_auth_headers(token),
        timeout=20,
    )
    data = resp.json()
    if resp.status_code >= 400:
        raise RuntimeError(data.get("detail") or "Failed to fetch users")
    return data.get("users", [])


def get_user_schedule(token: str, user_id: str) -> dict:
    resp = requests.get(
        f"{BACKEND_URL}/admin/users/{user_id}/schedule",
        headers=build_auth_headers(token),
        timeout=20,
    )
    data = resp.json()
    if resp.status_code >= 400:
        raise RuntimeError(data.get("detail") or "Failed to fetch user schedule")
    return data


def update_user_energy(token: str, user_id: str, energy_level: float) -> dict:
    resp = requests.patch(
        f"{BACKEND_URL}/admin/users/{user_id}/energy",
        json={"energy_level": energy_level},
        headers=build_auth_headers(token),
        timeout=20,
    )
    data = resp.json()
    if resp.status_code >= 400:
        raise RuntimeError(data.get("detail") or "Failed to update energy")
    return data


def create_user_task(token: str, user_id: str, payload: dict) -> dict:
    resp = requests.post(
        f"{BACKEND_URL}/admin/users/{user_id}/tasks",
        json=payload,
        headers=build_auth_headers(token),
        timeout=20,
    )
    data = resp.json()
    if resp.status_code >= 400:
        raise RuntimeError(data.get("detail") or "Failed to create task")
    return data


def update_task(token: str, task_id: str, payload: dict) -> dict:
    resp = requests.patch(
        f"{BACKEND_URL}/admin/tasks/{task_id}",
        json=payload,
        headers=build_auth_headers(token),
        timeout=20,
    )
    data = resp.json()
    if resp.status_code >= 400:
        raise RuntimeError(data.get("detail") or "Failed to update task")
    return data


def delete_task(token: str, task_id: str) -> None:
    resp = requests.delete(
        f"{BACKEND_URL}/admin/tasks/{task_id}",
        headers=build_auth_headers(token),
        timeout=20,
    )
    if resp.status_code >= 400:
        try:
            data = resp.json()
        except Exception:
            data = {"detail": resp.text}
        raise RuntimeError(data.get("detail") or "Failed to delete task")
