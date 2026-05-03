from ytee.rendering import render_table

import os
import time
from googleapiclient.discovery import build, Resource
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from rich.progress import Progress
from pathlib import Path


def build_upload_queue(file_path: str, yt_video_name: str) -> list[dict]:
    file_path_obj = Path(file_path)
    if file_path_obj.is_dir():
        return [
            {"path": str(file_path_obj.joinpath(video)), "name": f"{yt_video_name}{os.path.splitext(video)[0]}"}
            for video in [file for file in file_path_obj.iterdir() if file.is_file()]
        ]
    else:
        return [{"path": file_path, "name": yt_video_name}]


def upload_to_youtube(
    creds, file_path, yt_video_name, yt_video_description, task_dict, current_task_id, progress: Progress, live
) -> str:
    total = os.path.getsize(file_path)
    progress.start_task(current_task_id)
    youtube: Resource = build("youtube", "v3", credentials=creds)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {"title": yt_video_name, "description": yt_video_description},
            "status": {"privacyStatus": "unlisted"},
        },
        media_body=MediaFileUpload(file_path, chunksize=1024 * 1024, resumable=True),
    )
    response = None
    retries = 3
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                progress.update(current_task_id, completed=status.resumable_progress)
                live.update(render_table(task_dict, progress))
                live.refresh()
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
        progress.update(current_task_id, completed=total)
        live.update(render_table(task_dict, progress))
        live.refresh()
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
