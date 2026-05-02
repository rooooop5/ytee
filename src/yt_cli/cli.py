import json
import time
import os
import typer
from typing import Annotated

from yt_cli.auth import get_credentials, set_credentials, init_secrets
from yt_cli.upload import upload_to_youtube, build_upload_queue


app = typer.Typer(no_args_is_help=True)


@app.command()
def init(
    client_secret_path: Annotated[str, typer.Option("--secret-path", "-sp")] = None,
    token_path: Annotated[str, typer.Option("--token-path", "-tp")] = None,
):
    init_secrets(client_secret_path,token_path)


@app.command()
def set_creds():
    set = set_credentials()
    if set:
        print("Credentials have been set.")
    else:
        print("Failed to set credentials.")


@app.command()
def upload(
    file_path: Annotated[str, typer.Option("--path", "-p")],
    yt_video_name: Annotated[str, typer.Option("--name", "-n")],
    yt_description: Annotated[str, typer.Option("--desc", "-d")],
    directory: bool = typer.Option(False, "--is-dir"),
):
    creds = get_credentials()
    if not creds:
        print("Credentials have not been set. Aborting upload.")
        return
    if directory:
        queue = build_upload_queue(file_path)
        for video in queue:
            video_name = f"{yt_video_name}{os.path.splitext(video['name'])[0]}"
            video_id = upload_to_youtube(creds, video["path"], video_name, yt_description)
            if not video_id:
                print("Failed to upload to Youtube.")
                return
            with open("uploaded.txt", "a+") as f:
                f.write(f"{json.dumps({'path': f'{file_path}/{video["name"]}', 'id': video_id})}" + "\n")
            time.sleep(2)
    else:
        video_id = upload_to_youtube(creds, file_path, yt_video_name, yt_description)
        if not video_id:
            print("Failed to upload to Youtube")
            return
        with open("uploaded.txt", "a+") as f:
            f.write(f"{json.dumps({'path': file_path, 'id': video_id})}" + "\n")


@app.command()
def show_uploads():
    print("This is an upload")


if __name__ == "__main__":
    app()
