import requests


def registrer_user(telegram_id, name):
    return requests.post(
        "http://api:8000/users", json={"telegram_id": telegram_id, "name": name}
    )


def make_prompt(user_id, prompt):
    return requests.post(
        "http://api:8000/prompt", json={"user_id": user_id, "prompt": prompt}
    )
