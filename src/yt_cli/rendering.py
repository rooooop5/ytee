from rich.progress import Progress,TextColumn,BarColumn
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
import time
queue=["hi",'bue','me']

progress = Progress(
    TextColumn("{task.description}"),
    BarColumn(),
    TextColumn("{task.percentage:>3.0f}%"),
)
tasks={}

def add_tasks(queue):
    for video in queue:
        tasks[video]=progress.add_task(description=video,total=100)

def make_rich_table(queue):
    table=Table(title='Upload Queue')
    table.add_column('Video')
    table.add_column('Progress')
    for video in queue:
        bar=BarColumn()
        task_id=tasks[video]
        task=progress.tasks[task_id]
        table.add_row(video,bar.render(task))
    return table

add_tasks(queue)
table=make_rich_table(queue)

console=Console()
console.print(table)