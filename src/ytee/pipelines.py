from ytee.paths import get_uploads_dir
from ytee.auth import get_credentials, init_secrets, set_credentials, verify_credentials, migrate_secrets
from ytee.upload import build_upload_queue, upload_to_youtube
from ytee.rendering import get_progress, build_tasks_dict

import json
import time
from rich.live import Live
from pathlib import Path


def save(video: dict, file_path: str, video_id: str):
    uploaded_file_path = get_uploads_dir().joinpath("/uploaded.txt")
    if uploaded_file_path.is_dir():
        with open(uploaded_file_path, "a+") as f:
            f.write(f"{json.dumps({'path': Path(file_path).joinpath(video['name']), 'id': video_id})}" + "\n")
    else:
        with open(uploaded_file_path, "a+") as f:
            f.write(f"{json.dumps({'path': file_path, 'id': video_id})}" + "\n")


def migrate_pipeline():
    migrate_secrets()


def init_pipeline(client_secret_path: str, token_path_str):
    init_secrets(client_secret_path, token_path_str)


def set_creds_pipeline():
    set = set_credentials()
    if set:
        print("Credentials have been set.")
    else:
        print("Failed to set credentials.")


def verify_creds_pipeline():
    if verify_credentials():
        print("Credentials are already set.")
    else:
        print("Crendentials have not been set.")


def upload_pipeline(file_path: str, yt_video_name: str, yt_description: str, privacy_setting: str):
    creds = get_credentials()
    if not creds:
        print("Credentials have not been set. Aborting upload.")
        return
    queue = build_upload_queue(file_path, yt_video_name)
    with get_progress() as progress:
        tasks_dict = build_tasks_dict(queue, progress)
        with Live() as live:
            for video in queue:
                video_task = tasks_dict.get(video["path"])
                print(video["name"])
                video_id = upload_to_youtube(
                    creds,
                    video["path"],
                    video["name"],
                    yt_description,
                    privacy_setting,
                    tasks_dict,
                    video_task,
                    progress,
                    live,
                )
                if not video_id:
                    print("Failed to upload to Youtube.")
                    continue
                save(video, file_path, video_id)
                time.sleep(2)


def show_uploads_pipeline():
    uploaded_file_path = get_uploads_dir().joinpath("/uploaded.txt")
    if not uploaded_file_path.exists():
        print("No uploads have been done yet.")
        return
    with open(uploaded_file_path, "r") as f:
        print(f.read())
