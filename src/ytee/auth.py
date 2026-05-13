from ytee.paths import get_ytee_dir, get_secrets_dir, get_deprecated_secrets_dir

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from pathlib import Path


SCOPES = ["https://www.googleapis.com/auth/youtube"]


def init_secrets(client_secret_path: str = None, token_path: str = None):
    ytee_path_obj = get_ytee_dir()
    ytee_path_obj.mkdir(exist_ok=True)
    secrets_path = get_secrets_dir()
    secrets_path.mkdir(exist_ok=True)
    client_secret_destination = secrets_path.joinpath("client_secret.json")
    if not client_secret_destination.exists():
        if not client_secret_path:
            print("Client secret file path has not been provided for initialisation.")
            print("Failed to initialise ytee.")
            return
        client_secret_path_obj = Path(client_secret_path)
        client_secret_path_obj.rename(client_secret_destination)
    if token_path:
        token_path_obj = Path(token_path)
        token_destination = secrets_path.joinpath("token.json")
        token_path_obj.rename(token_destination)
    print("Initialised ytee.")


def browser_creds_flow(client_secret_path:Path)->Credentials|None:
    if not client_secret_path.exists():
        print("Client secret file does not exist.")
        return None
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file=client_secret_path, scopes=SCOPES)
    creds = flow.run_local_server(port=0)
    return creds


def set_credentials() -> bool:
    creds = None
    token_path = get_secrets_dir().joinpath("token.json")
    client_secret_path = get_secrets_dir().joinpath("client_secret.json")
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(token_path, scopes=SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except:
                creds = browser_creds_flow(client_secret_path)
                if not creds:
                    return False
        else:
            creds = browser_creds_flow(client_secret_path)
            if not creds:
                return False
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    return True


def verify_credentials() -> bool:
    secrets_path = get_secrets_dir()
    client_secret_path = get_secrets_dir().joinpath("client_secret.json")
    token_path = secrets_path.joinpath("token.json")
    if token_path.exists() and client_secret_path.exists():
        return True
    else:
        return False


def get_credentials() -> Credentials:
    secrets_path = get_secrets_dir()
    token_path = secrets_path.joinpath("token.json")
    if token_path.exists():
        try:
            return Credentials.from_authorized_user_file(token_path, scopes=SCOPES)
        except RefreshError:
            print("Your tokens have expired. Please refresh them using set-creds.")
            return None
    else:
        return None


def migrate_secrets():
    deprecated_client_secret_path = get_deprecated_secrets_dir().joinpath("client_secret.json")
    deprecated_token_path = get_deprecated_secrets_dir().joinpath("token.json")
    secrets_path = get_secrets_dir()
    new_client_secret_path = secrets_path.joinpath("client_secret.json")
    new_token_path = secrets_path.joinpath("token.json")
    if new_client_secret_path.exists() and new_token_path.exists():
        print("ytee is already set up, no need for migration.")
        return
    if not deprecated_client_secret_path.exists():
        print("Client secret file not found in ~/.secrets.")
        print("Failed to migrate.")
        return
    if not deprecated_token_path.exists():
        print("Token file not found at ~/.secrets.")
        print("Failed to migrate.")
        return
    deprecated_client_secret_path.rename(new_client_secret_path)
    deprecated_token_path.rename(new_token_path)
