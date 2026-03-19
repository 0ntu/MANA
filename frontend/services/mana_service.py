USE_MOCK = True

MOCK_MANA = {"current": 7.0, "max": 10.0, "status": "Good"}

MOCK_HISTORY = [
    {"id": "1", "energy_level": 8.0, "timestamp": "2024-03-13T09:00:00", "source": "manual"},
    {"id": "2", "energy_level": 5.0, "timestamp": "2024-03-13T13:00:00", "source": "manual"},
    {"id": "3", "energy_level": 3.0, "timestamp": "2024-03-13T18:00:00", "source": "manual"},
]

def get_mana_level(user_id):
    if USE_MOCK:
        return MOCK_MANA

def log_mana(user_id, level: float):
    if USE_MOCK:
        entry = {"id": str(len(MOCK_HISTORY) + 1), "energy_level": float(level), "timestamp": "now", "source": "manual"}
        MOCK_HISTORY.append(entry)
        return entry

def get_mana_history(user_id):
    if USE_MOCK:
        return MOCK_HISTORY