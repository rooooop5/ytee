from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from pathlib import Path
import os


SCOPES = ["https://www.googleapis.com/auth/youtube"]


def get_secrets_dir():
    home = Path.home()
    return Path(f"{home}/.secrets")


def init_secrets(client_secret_path=None,token_path=None):
    secrets_path = get_secrets_dir()
    if not secrets_path.exists():
        secrets_path.mkdir()
    client_secret_destination = Path(f"{secrets_path}/client_secret.json")
    if not client_secret_destination.exists():
        if not client_secret_path:
            print("Client secret file path has not been provided for initialisation.")
            print("Failed initialisation of yt-cli.")
            return
        client_secret_path_obj = Path(client_secret_path)
        client_secret_path_obj.rename(client_secret_destination)
    if token_path:
        token_path_obj=Path(token_path)
        token_destination=Path(f"{secrets_path}/token.json")
        token_path_obj.rename(token_destination)
    print("Initialised yt-cli.")


def set_credentials():
    creds = None
    secrets_path=get_secrets_dir()
    token_path=Path(f"{secrets_path}/token.json")
    client_secret=Path(f"{secrets_path}/client_secret.json")
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(token_path, scopes=SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not client_secret.exists():
                return False
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_file=client_secret, scopes=SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    return True


def get_credentials():
    secrets_path=get_secrets_dir()
    token_path=Path(f"{secrets_path}/token.json")
    if token_path.exists():
        return Credentials.from_authorized_user_file(token_path, scopes=SCOPES)
    else:
        return None
