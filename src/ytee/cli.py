from ytee.pipelines import (
    upload_pipeline,
    init_pipeline,
    set_creds_pipeline,
    show_uploads_pipeline,
    verify_creds_pipeline,
    migrate_pipeline,
)

import typer
from typing import Annotated

app = typer.Typer(no_args_is_help=True)


@app.command()
def init(
    client_secret_path: Annotated[str, typer.Option("--secret-path", "-s")] = None,
    token_path: Annotated[str, typer.Option("--token-path", "-t")] = None,
):
    init_pipeline(client_secret_path, token_path)


@app.command()
def migrate():
    migrate_pipeline()


@app.command()
def set_creds():
    set_creds_pipeline()


@app.command()
def verify_creds():
    verify_creds_pipeline()


@app.command()
def upload(
    file_path: Annotated[str, typer.Option("--path", "-p")],
    yt_video_name: Annotated[str, typer.Option("--name", "-n")],
    yt_description: Annotated[str, typer.Option("--desc", "-d")],
    privacy: Annotated[str, typer.Option("--privacy")] = "unlisted",
):
    upload_pipeline(file_path, yt_video_name, yt_description, privacy)


@app.command()
def show_uploads():
    show_uploads_pipeline()


if __name__ == "__main__":
    app()
