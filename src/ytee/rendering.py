from ytee.models import TaskInfo, RenderingColumns

from rich.progress import Progress
from rich.table import Table
from rich.console import Console

console = Console()


def get_progress(columns: RenderingColumns) -> Progress:
    progress = Progress(
        columns.spinner_column,
        columns.bar_column,
        columns.file_size_column,
        columns.total_file_size_column,
        columns.time_elapsed_column,
        columns.time_remaining_column,
        columns.download_column,
        console=console,
        disable=True,
    )
    return progress


def render_table(task_dict: dict[str, TaskInfo], progress: Progress, columns: RenderingColumns) -> Table:
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
            columns.bar_column.render(task),
            columns.file_size_column.render(task),
            columns.total_file_size_column.render(task),
            columns.time_elapsed_column.render(task),
            columns.time_remaining_column.render(task),
            columns.download_column.render(task),
        )
    return table
