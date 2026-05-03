from pathlib import Path


def get_home() -> Path:
    return Path.home()


def get_ytee_dir() -> Path:
    return get_home().joinpath(".ytee")


def get_secrets_dir() -> Path:
    return get_home().joinpath(get_ytee_dir()).joinpath(".google_secrets")


def get_uploads_dir() -> Path:
    return get_home().joinpath(get_ytee_dir()).joinpath(".uploads")
