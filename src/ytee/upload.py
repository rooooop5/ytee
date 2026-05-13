from ytee.models import (
    FileInfo,
    YoutubeUploadConfig,
    DisplayManager,
    TasksRegistry,
    TaskInfo,
    ControlSignal,
    UploadRetryConfig,
)

from ssl import SSLError
from googleapiclient.discovery import build, Resource
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from httplib2.error import ServerNotFoundError
from pathlib import Path


def handle_http_errors(e: HttpError, retries: int) -> ControlSignal:
    signal = ControlSignal.NORMAL
    if e.resp.status == 403:
        print("API quota exceeded.")
        print("Reason:", e.reason)
        print("Error details:", e.error_details)
        signal = ControlSignal.BREAK
    elif e.resp.status == 401:
        print("Token expired during upload. Run set-creds to refresh token.")
        print("Reason:", e.reason)
        print("Error details:", e.error_details)
        signal = ControlSignal.BREAK
    elif e.resp.status == 400:
        print("Bad request.")
        print("Reason:", e.reason)
        print("Error details:", e.error_details)
        signal = ControlSignal.BREAK
    elif e.resp.status >= 500 and retries > 0:
        signal = ControlSignal.CONTINUE
    elif retries <= 0:
        print("Retries depleted.")
        signal = ControlSignal.BREAK
    else:
        print("fatal error:", e.resp.status)
        print(e.error_details if hasattr(e, "error_details") else str(e))
        signal = ControlSignal.BREAK
    return signal


def handle_network_errors(retries: int) -> ControlSignal:
    if retries < 0:
        return ControlSignal.BREAK
    else:
        return ControlSignal.CONTINUE


def build_upload_queue(file_path: str, yt_video_name: str) -> list[FileInfo]:
    SUPPORTED_EXTENSIONS = {".mp4", ".mov", ".avi", ".wmv", ".mkv", ".webm", ".m4v", ".mpeg", ".mpg", ".flv"}
    file_path_obj = Path(file_path)
    if file_path_obj.is_dir():
        queue = [
            FileInfo(path=file, name=yt_video_name + file.stem)
            for file in file_path_obj.iterdir()
            if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS
        ]
        if not queue:
            print("There are no supported videos in this directory.")
        return queue
    if file_path_obj.suffix.lower() in SUPPORTED_EXTENSIONS:
        return [FileInfo(path=file_path_obj, name=yt_video_name)]
    print("File of this format is not supported.")
    return []


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
    retry_config = UploadRetryConfig()
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                registry.update(task, status.resumable_progress)
                display.refresh()
        except HttpError as e:
            signal = handle_http_errors(e=e, retries=retry_config.http_retries)
            if signal == ControlSignal.BREAK:
                break
            elif signal == ControlSignal.CONTINUE:
                retry_config.wait(exception_type="HTTP")
        except (TimeoutError, SSLError, OSError, ConnectionResetError) as e:
            signal = handle_network_errors(retries=retry_config.network_retries)
            if signal == ControlSignal.BREAK:
                break
            elif signal == ControlSignal.CONTINUE:
                retry_config.wait(exception_type="NETWORK")
        except ServerNotFoundError as e:
            print(e)
            print("Check your internet connnection.")
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
