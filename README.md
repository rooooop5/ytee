# ytee

A minimal CLI for uploading videos to YouTube — single files or entire directories, powered by the YouTube Data API v3.

---

## Quickstart

```
ytee init → ytee set-creds → ytee upload
```

These three commands are all you need. **`init` must be run before anything else.**

---

## Setup

### 1. Get Google API credentials

Before using `ytee`, you need a Google Cloud project with the YouTube Data API v3 enabled:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **YouTube Data API v3**.
3. Create **OAuth 2.0 credentials** for a Desktop application.
4. Download the credentials as a JSON file (e.g. `client_secret.json`).

### 2. Install ytee

```bash
pip install ytee 
```

---

## CLI commands

### `ytee init` — **Run this first**

Copies your Google OAuth credentials into `~/.secrets/` so `ytee` can find them.

```bash
ytee init --secret-path /path/to/client_secret.json
```

```
Options:
  -sp, --secret-path    Path to your client_secret.json (required on first run)
  -tp, --token-path     Path to an existing token.json (optional)
```

> ⚠️ This must be run at least once before any other command will work.

---

### `ytee set-creds` — Authenticate with Google

Opens a browser window for Google OAuth authorization and saves the access token to `~/.secrets/token.json`.

```bash
ytee set-creds
```

Run this after `init`. If your credentials are still valid, it reuses them automatically.

---

### `ytee upload` — Upload a video or directory

**Upload a single video:**

```bash
ytee upload --path video.mp4 --name "My Video Title" --desc "My description"
```

**Upload all videos in a directory:**

```bash
ytee upload --path ./videos --name "Episode - " --desc "My description" --is-dir
```

When uploading a directory, each filename is appended to the `--name` prefix to form the video title. For example, if the directory contains `part1.mp4`, the title becomes `Episode - part1`.

```
Options:
  -p, --path      Path to a video file or directory
  -n, --name      YouTube video title (used as a prefix for directory uploads)
  -d, --desc      YouTube video description
      --is-dir    Treat --path as a directory and upload all files inside it
```

After each successful upload, `ytee` logs the file path and YouTube video ID to `uploaded.txt` in your current directory:

```
{"path": "videos/part1.mp4", "id": "abc123XYZ"}
```

---

### `ytee show-uploads` — View upload history

```bash
ytee show-uploads
```

Shows previously uploaded videos from the local `uploaded.txt` log.

---

## Full example walkthrough

```bash
# Step 1 — point ytee to your Google credentials (once)
ytee init --secret-path ~/Downloads/client_secret.json

# Step 2 — authenticate with Google (once, or when token expires)
ytee set-creds

# Step 3a — upload a single video
ytee upload --path ~/videos/intro.mp4 --name "Introduction" --desc "Welcome to my channel"

# Step 3b — or upload a whole folder
ytee upload --path ~/videos --name "Lecture - " --desc "Course upload" --is-dir
```

---

## Notes

- Videos are uploaded as **unlisted** by default.
- Secrets are stored in `~/.secrets/` (`client_secret.json` and `token.json`).
- Directory uploads process files sequentially with a short delay between each upload.
- Batch uploads currently include all files in the directory regardless of extension.

## Requirements

- Python 3.9+
- YouTube Data API v3 enabled on a Google Cloud project