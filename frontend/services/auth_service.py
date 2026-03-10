#we can set mock to false when we have the real users
USE_MOCK = True

def login(username, password):
    if USE_MOCK:
        mock_users = {"student1": "pass123", "athlete1": "pass456"}
        return mock_users.get(username) == password
    # TODO: POST /auth/login

def get_current_user():
    if USE_MOCK:
        return {"id": "u1", "name": "Alex", "role": "student", "mana": 7}
    # TODO: GET /users/me