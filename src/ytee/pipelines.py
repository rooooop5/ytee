from ytee.models import YoutubeUploadConfig, UploadLog, DisplayManager, TasksRegistry, RenderingColumns
from ytee.paths import get_uploads_dir
from ytee.auth import get_credentials, init_secrets, set_credentials, verify_credentials, migrate_secrets
from ytee.upload import build_upload_queue, upload_to_youtube
from ytee.rendering import get_progress, render_table

import json
import time
from pprint import pprint
from rich.live import Live


def save(log: UploadLog):
    file_path = log.file_path
    uploads_dir = get_uploads_dir()
    uploads_dir.mkdir(exist_ok=True)
    uploads_file_path = get_uploads_dir().joinpath("uploaded.json")
    try:
        with open(uploads_file_path, "r") as f:
            uploaded_list = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        uploaded_list = []
    with open(uploads_file_path, "w+") as f:
        obj = {"path": file_path, "youtube_video_name": log.name, "id": log.id}
        uploaded_list.append(obj)
        json.dump(uploaded_list, f, indent=2)


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
    columns = RenderingColumns()
    with get_progress(columns) as progress:
        tasks_registry = TasksRegistry(queue=queue, progress=progress)
        with Live() as live:
            display_manager = DisplayManager(live=live, renderer=render_table, registry=tasks_registry, columns=columns)
            for video in queue:
                task = tasks_registry.get(video.path)
                tasks_registry.start_task(task)
                config = YoutubeUploadConfig(
                    name=video.name, description=yt_description, privacy_setting=privacy_setting
                )
                response_id = upload_to_youtube(
                    creds=creds,
                    video=video,
                    config=config,
                    display=display_manager,
                    registry=tasks_registry,
                    task=task,
                )
                if not response_id:
                    print("Failed to upload to Youtube.")
                    continue
                tasks_registry.finish_task(task_info=task)
                display_manager.refresh()
                upload_log = UploadLog(file_path=video.path, name=config.name, id=response_id)
                save(upload_log)
                time.sleep(2)


def show_uploads_pipeline():
    uploaded_file_path = get_uploads_dir().joinpath("uploaded.json")
    if not uploaded_file_path.exists():
        print("No uploads have been done yet.")
        return
    with open(uploaded_file_path, "r") as f:
        uploaded_list = json.load(f)
        pprint(uploaded_list)
