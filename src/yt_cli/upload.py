from googleapiclient.discovery import build, Resource
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import time
from rich.progress import Progress
import os


def build_upload_queue(dir_path):
    return [{"path": os.path.join(dir_path, video),'name':video} for video in os.listdir(dir_path)]
    return [{"path": os.path.join(dir_path, video),'name':video, "tries": 3,'status':'PENDING'} for video in os.listdir(dir_path)]


def upload_to_youtube(creds, file_path,yt_video_name,yt_video_description):
    with Progress() as progress:
        task=progress.add_task(f'{yt_video_name}',total=os.path.getsize(file_path)/(1024*1024))
        youtube: Resource = build("youtube", "v3", credentials=creds)
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {"title":yt_video_name, "description":yt_video_description},
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
                    progress.update(task,completed=status.resumable_progress/(1024*1024))
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
                    print(e.error_details if hasattr(e,"error_details") else str(e))
                    break
        progress.remove_task(task)
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
