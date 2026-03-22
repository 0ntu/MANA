import requests

from services.auth_service import BACKEND_URL, build_auth_headers


def log_energy(token: str, energy_level: float) -> dict:
    """
    Logs a mana/energy entry via backend POST `/energy/log`.
    """
    url = f"{BACKEND_URL}/energy/log"
    resp = requests.post(
        url,
        json={"energy_level": float(energy_level)},
        headers=build_auth_headers(token),
        timeout=20,
    )
    try:
        data = resp.json()
    except Exception:
        data = {"detail": resp.text}

    if resp.status_code >= 400:
        raise RuntimeError(data.get("detail") or "Failed to log energy")
    return data

