from enum import Enum
from rich.live import Live
from rich.progress import Progress, TaskID
from pathlib import Path
from dataclasses import dataclass


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
    def __init__(self, live: Live, renderer: callable, registry: TasksRegistry):
        self.live = live
        self.renderer = renderer
        self.registry = registry

    def refresh(self):
        self.live.update(self.renderer(self.registry.tasks, self.registry.progress))
        self.live.refresh()
