import time
import psutil
from collections import deque
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Constants
HISTORY_SIZE = 50
BAR_WIDTH = 30

class SystemMonitor:
    def __init__(self, history_size: int = HISTORY_SIZE):
        self.history_size = history_size
        self.cpu_history = deque(maxlen=history_size)
        self.ram_history = deque(maxlen=history_size)
        self.ram_used_gb = 0.0
        self.ram_total_gb = 0.0

    def update_stats(self):
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        ram_percent = mem.percent
        self.ram_used_gb = mem.used / (1024 ** 3)
        self.ram_total_gb = mem.total / (1024 ** 3)

        self.cpu_history.append(cpu)
        self.ram_history.append(ram_percent)

        return cpu, ram_percent

    def make_bar(self, percentage: float, width: int = BAR_WIDTH) -> Text:
        filled = int(width * (percentage / 100))
        empty = width - filled
        bar_str = "█" * filled + "░" * empty
        color = "green"
        if percentage > 80:
            color = "yellow"
        if percentage > 90:
            color = "red"
        return Text(f"[{bar_str}] {percentage:>5.1f}%", style=color)

    def render_graph(self, history, label: str):
        if not history:
            graph = " " * self.history_size
        else:
            normalized = [int((val / 100) * 10) for val in history]
            blocks = " ▁▂▃▄▅▆▇█"
            graph = "".join(blocks[n] if n < len(blocks) else blocks[-1] for n in normalized)
        return f"{label}: [{graph.rjust(self.history_size)}]"

    def get_display(self) -> Panel:
        cpu, ram = self.update_stats()
        ram_abs_str = f"{self.ram_used_gb:.1f} / {self.ram_total_gb:.1f} GiB"

        cpu_graph = self.render_graph(self.cpu_history, "CPU")
        ram_graph = self.render_graph(self.ram_history, "RAM")

        table = Table.grid(padding=(0, 1))
        table.add_row("[bold]CPU Usage[/bold]")
        table.add_row(self.make_bar(cpu))
        table.add_row(cpu_graph)
        table.add_row("")
        table.add_row("[bold]RAM Usage[/bold]")
        table.add_row(self.make_bar(ram))
        table.add_row(f"[dim]{ram_abs_str}[/dim]")
        table.add_row(ram_graph)

        return Panel(table, title="System Monitor", border_style="cyan")

def main():
    monitor = SystemMonitor()
    console = Console()

    console.print("[bold cyan]Starting real-time system monitor... Press Ctrl+C to exit.[/bold cyan]\n")

    try:
        with Live(monitor.get_display(), refresh_per_second=4, console=console) as live:
            while True:
                live.update(monitor.get_display())
                time.sleep(0.25)
    except KeyboardInterrupt:
        console.print("\n[bold red]Monitoring stopped.[/bold red]")

if __name__ == "__main__":
    main()