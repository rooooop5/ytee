from ytee.models import (
    FileInfo,
    YoutubeUploadConfig,
    DisplayManager,
    TasksRegistry,
    TaskInfo,
)

import time
from googleapiclient.discovery import build, Resource
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from pathlib import Path


def build_upload_queue(file_path: str, yt_video_name: str) -> list[FileInfo]:
    file_path_obj = Path(file_path)
    if file_path_obj.is_dir():
        return [
            FileInfo(path=file_path_obj.joinpath(video), name=yt_video_name + Path(video).stem)
            for video in [file for file in file_path_obj.iterdir() if file.is_file()]
        ]
    else:
        return [FileInfo(path=Path(file_path), name=yt_video_name)]


def upload_to_youtube(
    creds,
    video: FileInfo,
    config: YoutubeUploadConfig,
    task: TaskInfo,
    registry: TasksRegistry,
    display: DisplayManager,
) -> str:
    youtube: Resource = build("youtube", "v3", credentials=creds)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {"title": config.name, "description": config.description},
            "status": {"privacyStatus": config.privacy_setting},
        },
        media_body=MediaFileUpload(video.path, chunksize=1024 * 1024, resumable=True),
    )
    response = None
    retries = 3
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                registry.update(task, status.resumable_progress)
                display.refresh()
        except HttpError as e:
            if e.resp.status >= 500 and retries > 0:
                retries -= 1
                time.sleep(5)
                continue
            elif retries <= 0:
                print("Retries depleted.")
                break
            else:
                print(f"fatal error:{e.resp.status}")
                print(e.error_details if hasattr(e, "error_details") else str(e))
                break
    if response and "id" in response:
        return response["id"]
    else:
        return None


def add_to_playlist(creds, video_id, playlist_id):
    youtube = build("youtube", "v3", credentials=creds)
    request = youtube.playlistItems().insert(
        part="snippet",
        body={"snippet": {"playlistId": playlist_id, "resourceId": {"kind": "youtube#video", "videoId": video_id}}},
    )
    response = request.execute()
    return response
