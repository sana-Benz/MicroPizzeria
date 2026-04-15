import requests
from flask import current_app

def validate_token(token):
    url = f"{current_app.config['USER_SERVICE_URL']}/auth/validate"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return None