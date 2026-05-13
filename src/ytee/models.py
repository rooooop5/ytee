from enum import Enum
from rich.live import Live
from rich.progress import (
    Progress,
    TaskID,
    BarColumn,
    SpinnerColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    TotalFileSizeColumn,
    FileSizeColumn,
    DownloadColumn,
)
import time
from pathlib import Path
from typing import Literal
from dataclasses import dataclass, field


@dataclass
class UploadRetryConfig:
    network_retries: int = 10
    http_retries: int = 5
    wait_seconds: int = 2

    def wait(self, exception_type: Literal["HTTP", "NETWORK"]):
        if exception_type == "HTTP":
            self.http_retries -= 1
        elif exception_type == "NETWORK":
            self.network_retries -= 1
        time.sleep(self.wait_seconds)
        self.wait = min(self.wait**2, 30)


class ControlSignal(str, Enum):
    BREAK = "BREAK"
    CONTINUE = "CONTINUE"
    NORMAL = "NORMAL"


class PrivacySetting(str, Enum):
    UNLISTED = "unlisted"
    PRIVATE = "private"
    PUBLIC = "public"


@dataclass
class YoutubeUploadConfig:
    name: str
    description: str
    privacy_setting: str


class FileInfo:
    def __init__(self, path: Path, name: str):
        self.path = str(path)
        self.name = name
        self.file_size = path.stat().st_size


@dataclass
class UploadLog:
    file_path: str
    name: str
    id: str


@dataclass
class TaskInfo:
    task_id: TaskID
    total: int


@dataclass
class RenderingColumns:
    spinner_column: SpinnerColumn = field(default_factory=SpinnerColumn)
    bar_column: BarColumn = field(default_factory=BarColumn)
    total_file_size_column: TotalFileSizeColumn = field(default_factory=TotalFileSizeColumn)
    file_size_column: FileSizeColumn = field(default_factory=FileSizeColumn)
    time_remaining_column: TimeRemainingColumn = field(default_factory=TimeRemainingColumn)
    time_elapsed_column: TimeElapsedColumn = field(default_factory=TimeElapsedColumn)
    download_column: DownloadColumn = field(default_factory=DownloadColumn)


class TasksRegistry:
    def __init__(self, queue: list[FileInfo], progress: Progress):
        self.progress = progress
        self.tasks = {}

        for file_info in queue:
            total = file_info.file_size
            task_id = self.progress.add_task(file_info.path, start=False, total=total)
            self.tasks[file_info.path] = TaskInfo(task_id=task_id, total=total)

    def get(self, path: str) -> TaskInfo:
        return self.tasks.get(path)

    def start_task(self, task_info: TaskInfo):
        self.progress.start_task(task_info.task_id)

    def update(self, task_info: TaskInfo, completed: int):
        self.progress.update(task_info.task_id, completed=completed)

    def finish_task(self, task_info: TaskInfo):
        self.progress.update(task_info.task_id, completed=task_info.total)


class DisplayManager:
    def __init__(self, live: Live, renderer: callable, registry: TasksRegistry, columns: RenderingColumns):
        self.live = live
        self.renderer = renderer
        self.registry = registry
        self.columns = columns

    def refresh(self):
        self.live.update(self.renderer(self.registry.tasks, self.registry.progress, self.columns))
        self.live.refresh()
