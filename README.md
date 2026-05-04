<p align="center">
<img src="assets/ytee_logo.png" alt="ytee logo" width="600"/>
</p>

# ytee

A minimal CLI tool for uploading videos to YouTube — single files or entire directories — powered by the YouTube Data API v3.

---

## Quickstart

```bash
ytee init → ytee set-creds → ytee upload
```

These three commands are all you need. **`init` must be run before anything else.**

---

## Installation

```bash
pip install ytee
```

Requires **Python 3.9+**.

---

## Setup

### 1. Get Google API credentials

Before using `ytee`, you need a Google Cloud project with the YouTube Data API v3 enabled:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **YouTube Data API v3**.
3. Create **OAuth 2.0 credentials** for a Desktop application.
4. Download the credentials as a JSON file (e.g. `client_secret.json`).

### Migration from v0.1.0

If you used `ytee` version `v0.1.0`, your credentials were stored under `~/.secrets/`. In newer versions, `ytee` now stores credentials in `~/.ytee/.google_secrets/`.

Run the migration command once before using `ytee` :

```bash
ytee migrate
```

This moves `client_secret.json` and `token.json` from `~/.secrets/` into the current `ytee` secrets directory.

---

## CLI Commands

### `ytee init` — Run this first

Copies your Google OAuth credentials into `~/.ytee/.google_secrets/` so `ytee` can find them.

```bash
ytee init --secret-path /path/to/client_secret.json
```

| Option | Short | Description |
|---|---|---|
| `--secret-path` | `-sp` | Path to your `client_secret.json` (required on first run) |
| `--token-path` | `-tp` | Path to an existing `token.json` (optional) |

> ⚠️ This must be run at least once before any other command will work.

---

### `ytee set-creds` — Authenticate with Google

Opens a browser window for Google OAuth authorization and saves the access token to `~/.ytee/.google_secrets/token.json`.

```bash
ytee set-creds
```

Run this after `init`. If your credentials are still valid, they are reused automatically.

---

### `ytee verify-creds` — Check credential status

Checks whether both `client_secret.json` and `token.json` are present.

```bash
ytee verify-creds
```

---

### `ytee upload` — Upload a video or directory

**Upload a single video:**

```bash
ytee upload --path video.mp4 --name "My Video Title" --desc "My description"
```

**Upload all videos in a directory:**

```bash
ytee upload --path ./videos --name "Episode - " --desc "My description"
```

When a directory path is given, `ytee` automatically detects it and uploads every file inside. Each filename (without extension) is appended to the `--name` prefix to form the video title. For example, if the directory contains `part1.mp4`, the title becomes `Episode - part1`.

| Option | Short | Description |
|---|---|---|
| `--path` | `-p` | Path to a video file or directory |
| `--name` | `-n` | YouTube video title (used as a prefix for directory uploads) |
| `--desc` | `-d` | YouTube video description |

After each successful upload, `ytee` appends a log entry to `~/.ytee/.uploads/uploaded.txt`:

```json
{"path": "videos/part1.mp4", "id": "abc123XYZ"}
```

Uploads show a live progress table displaying upload speed, file size, time elapsed, and time remaining.

---

### `ytee show-uploads` — View upload history

```bash
ytee show-uploads
```

Prints the full contents of the upload log at `~/.ytee/.uploads/uploaded.txt`.

---

## Full Example Walkthrough

```bash
# Step 1 — point ytee to your Google credentials (once)
ytee init --secret-path ~/Downloads/client_secret.json

# Step 2 — authenticate with Google (once, or when token expires)
ytee set-creds

# Step 3 — check credentials are in place (optional)
ytee verify-creds

# Step 4a — upload a single video
ytee upload --path ~/videos/intro.mp4 --name "Introduction" --desc "Welcome to my channel"

# Step 4b — or upload a whole folder
ytee upload --path ~/videos --name "Lecture - " --desc "Course upload"
```

---

## Notes

- Videos are uploaded as **unlisted** by default.
- Credentials are stored in `~/.ytee/.google_secrets/` (`client_secret.json` and `token.json`).
- Upload history is stored in `~/.ytee/.uploads/uploaded.txt`.
- Directory uploads process files sequentially with a short delay between each upload.
- Batch uploads include all files in the directory regardless of file extension.
- On HTTP 5xx errors, `ytee` will retry the upload up to 3 times with a 5-second delay.

---

## Dependencies

| Package | Purpose |
|---|---|
| `google-api-python-client` | YouTube Data API v3 client |
| `google-auth-oauthlib` | OAuth 2.0 authentication flow |
| `rich` | Live progress table and terminal output |
| `typer` | CLI framework |
| `pathlib` | Path handling |