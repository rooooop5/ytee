from ytee.models import TaskInfo

from rich.progress import (
    Progress,
    BarColumn,
    SpinnerColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    TotalFileSizeColumn,
    FileSizeColumn,
    DownloadColumn,
)
from rich.table import Table
from rich.console import Console


console = Console()
spinner_column = SpinnerColumn()
bar_column = BarColumn()
total_file_size_column = TotalFileSizeColumn()
file_size_column = FileSizeColumn()
time_remaining_column = TimeRemainingColumn()
time_elapsed_column = TimeElapsedColumn()
download_column = DownloadColumn()


def get_progress() -> Progress:
    progress = Progress(
        spinner_column,
        bar_column,
        file_size_column,
        total_file_size_column,
        time_elapsed_column,
        time_remaining_column,
        download_column,
        console=console,
        disable=True,
    )
    return progress


def render_table(task_dict: dict[str, TaskInfo], progress:Progress) -> Table:
    table = Table(title="UPLOADS")
    table.add_column("Video", justify="center")
    table.add_column("Progress Bar", justify="center")
    table.add_column("Size Uploaded", justify="center")
    table.add_column("Total File Size", justify="center")
    table.add_column("Time Elapsed", justify="center")
    table.add_column("Time Remaining", justify="center")
    table.add_column("Uploaded", justify="center")
    for task_name, task_info in task_dict.items():
        task = progress.tasks[task_info.task_id]
        table.add_row(
            task_name,
            bar_column.render(task),
            file_size_column.render(task),
            total_file_size_column.render(task),
            time_elapsed_column.render(task),
            time_remaining_column.render(task),
            download_column.render(task),
        )
    return table
