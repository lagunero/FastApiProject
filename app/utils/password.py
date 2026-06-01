DEMO_CREDENTIALS = {
    "user": "password",
    "admin": "password",
}


def verify_demo_credentials(username: str, password: str) -> bool:
    return DEMO_CREDENTIALS.get(username) == password
