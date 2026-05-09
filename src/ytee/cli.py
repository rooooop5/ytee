from ytee.pipelines import (
    upload_pipeline,
    init_pipeline,
    set_creds_pipeline,
    show_uploads_pipeline,
    verify_creds_pipeline,
    migrate_pipeline,
)
from ytee.models import PrivacySetting

import typer
from typing import Annotated

app = typer.Typer(no_args_is_help=True)


@app.command(
    help="Initialize ytee by copying your Google OAuth credentials into ~/.ytee. Run this once before anything else.",
)
def init(
    client_secret_path: Annotated[
        str,
        typer.Option(
            "--secret-path", "-s", help="Path to your client secret file downloaded from Google Cloud Console."
        ),
    ] = None,
    token_path: Annotated[
        str,
        typer.Option(
            "--token-path", "-t", help="Path to an existing token.json, optional — skip if you don't have one yet."
        ),
    ] = None,
):
    init_pipeline(client_secret_path, token_path)


@app.command(
    help="Move old Google OAuth files from ~/.secrets/ into ~/.ytee/.google_secrets/ for newer ytee versions. Run this command only if previous ytee versions were initialised using init command.",
)
def migrate():
    migrate_pipeline()


@app.command(
    help="Authenticate with Google via OAuth. Opens a browser window and saves the access token to ~/.ytee/.google_secrets/token.json.",
)
def set_creds():
    set_creds_pipeline()


@app.command(
    help="Check whether your credentials are in place. Confirms that token.json exist in ~/.ytee/.google_secrets/.",
)
def verify_creds():
    verify_creds_pipeline()


@app.command(
    no_args_is_help=True,
    help="Upload a video or a directory of videos to YouTube. Pass a file path to upload a single video, or a directory path to upload everything inside it.",
)
def upload(
    file_path: Annotated[str, typer.Option("--path", "-p", help="Path to a video file or a directory of videos.")],
    yt_video_name: Annotated[
        str,
        typer.Option(
            "--name",
            "--prefix",
            "-n",
            help="YouTube video title. For directory uploads this is used as a prefix — the filename is appended automatically.",
        ),
    ],
    yt_description: Annotated[
        str, typer.Option("--desc", "-d", help="YouTube video description applied to all uploaded videos.")
    ],
    privacy: Annotated[
        PrivacySetting, typer.Option("--privacy", help="Privacy setting of the video on Youtube")
    ] = PrivacySetting.UNLISTED,
):
    upload_pipeline(file_path, yt_video_name, yt_description, privacy)


@app.command(
    help="Print the upload history log stored at ~/.ytee/.uploads/uploaded.txt, showing the file path and YouTube video ID of every past upload.",
)
def show_uploads():
    show_uploads_pipeline()


if __name__ == "__main__":
    app()
