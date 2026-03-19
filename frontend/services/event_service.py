USE_MOCK = True
from datetime import datetime

MOCK_EVENTS = [
    {"id": "1", "title": "CEN3031 Lecture", "description": "Weekly lecture", "scheduled_time": "2024-03-11T10:00:00", "energy_cost": 3.0, "status": "planned"},
    {"id": "2", "title": "Soccer Practice", "description": "Team practice", "scheduled_time": "2024-03-12T15:00:00", "energy_cost": 5.0, "status": "planned"},
    {"id": "3", "title": "Study Group", "description": "", "scheduled_time": "2024-03-13T18:00:00", "energy_cost": 2.0, "status": "completed"},
]

def get_events(user_id):
    if USE_MOCK:
        return MOCK_EVENTS

def add_event(user_id, event):
    if USE_MOCK:
        event["id"] = str(len(MOCK_EVENTS) + 1)
        event["status"] = "planned"
        MOCK_EVENTS.append(event)
        return event
   

def update_event(event_id, updated_fields):
    if USE_MOCK:
        for e in MOCK_EVENTS:
            if e["id"] == event_id:
                e.update(updated_fields)
                return e
    
def delete_event(event_id):
    if USE_MOCK:
        global MOCK_EVENTS
        MOCK_EVENTS = [e for e in MOCK_EVENTS if e["id"] != event_id]
        return True
    