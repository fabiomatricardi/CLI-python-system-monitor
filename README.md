# CLI-python-system-monitor
a small CLI app in python with EXE package to monitor CPU/RAM

You can create a real-time system monitor CLI app using Python's `rich` library along with `psutil` to fetch CPU and RAM usage. The `rich` library supports live updating displays via its `Live` context manager, which allows you to redraw parts of the terminal while keeping other parts static.

Below is a clean, modular implementation that:
- Displays live CPU and RAM usage bars.
- Shows usage history as simple ASCII graphs.
- Keeps the monitoring UI in a dedicated, boxed panel.
- Runs independently while allowing you to add your own logic in the main loop.

---

### ✅ Requirements
Install the required packages:

```bash
pip install rich psutil
```

---

### 🧠 Implementation

```python
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
```

---

### 🔍 Features

- **Live Updating:** The `Live` context manager redraws only the monitor panel.
- **Graph Visualization:** Uses block characters to show usage trends over time.
- **Non-blocking:** You can insert your own app logic in the `while True` loop.
- **Clean UI:** Uses `rich` panels, tables, and progress bars for an elegant terminal interface.

---

### 💡 Tip: Add Your Own Logic

If you want to run your own operations while monitoring continues, just add your code inside the `while True` loop:

```python
while True:
    # Your custom logic here (e.g., processing files, API calls, etc.)
    do_something()
    
    # Keep monitor updated
    live.update(monitor.get_display())
    time.sleep(0.25)
```

You can **package your Python script into a standalone `.exe` file** for Windows using tools like **PyInstaller**, which is the most popular and reliable option for this task.

Since our app uses:
- `rich`
- `psutil`
- Standard library modules (`time`, `collections`, etc.)

…it will work perfectly with PyInstaller.

---

### ✅ Step-by-Step Guide to Make a `.exe`

#### 1. **Install PyInstaller**
Open a terminal (Command Prompt or PowerShell) in your project directory and run:

```bash
pip install pyinstaller
```

> Make sure you're in the same Python environment where `rich` and `psutil` are installed.

---

#### 2. **Create the Executable**

Assuming your script is named `system_monitor.py`, run:

```bash
pyinstaller --onefile --console system_monitor.py
```

**Explanation:**
- `--onefile`: Bundles everything into a single `.exe` (easier to share).
- `--console`: Keeps the console window open (required because your app is CLI-based and uses terminal output).
  - ⚠️ **Do NOT use `--noconsole`** — your app needs the terminal for `rich` to render.

> The first build may take a minute or two as PyInstaller analyzes dependencies.

---

#### 3. **Find Your `.exe`**

After it finishes, the executable will be in the `dist/` folder:

```
your-project/
├── system_monitor.py
├── dist/
│   └── system_monitor.exe   ← This is your app!
├── build/
└── system_monitor.spec
```

Just run `system_monitor.exe` — it should open a terminal and show your live monitor!

---

### 🔒 Notes & Tips

#### ✅ It will work offline
Once built, the `.exe` includes Python, your code, and all dependencies — no need for the user to have Python installed.

#### 📦 File size
The `.exe` will be **~30–50 MB** because it bundles Python and libraries. This is normal.

#### 🛡️ Antivirus false positives
Sometimes PyInstaller-packaged apps trigger false positives in antivirus software (because they unpack code in memory). If this happens:
- Add an exception in your AV.
- Consider code-signing for distribution (advanced).

#### 🧪 Test it
Always test the `.exe` on a clean Windows machine (or VM) without Python installed to confirm it works standalone.

---

### ✅ Summary

| Step | Command |
|------|--------|
| Install PyInstaller | `pip install pyinstaller` |
| Build .exe | `pyinstaller --onefile --console your_script.py` |
| Run | `dist/your_script.exe` |

You now have a portable Windows `.exe` of your real-time system monitor! 🎉

Let me know if you want an icon, a custom name, or a silent background version (though `rich` needs a console, so background mode isn’t ideal).
