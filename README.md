# Auto Save Monitor

Automatically monitors a game process and backs up save files/folders while the game is running.

## Features

- **Auto Backup**: Creates timestamped backups every N seconds when game is running
- **Smart Backups**: Only backs up when files/folders have changed (MD5 hash comparison)
- **File & Folder Support**: Back up single files or entire directories
- **FIFO Management**: Automatically removes oldest backups when limit reached
- **GUI & CLI**: Both graphical and command-line interfaces
- **Cross-platform**: Works on macOS and Linux

## Installation

```bash
# Clone repository
git clone <repo-url>
cd Auto_saver

# Install with uv (recommended)
uv venv
source .venv/bin/activate  # On Linux/Mac
# OR
uv sync

# Install tkinter (for GUI)
# macOS: Usually pre-installed
# Linux: sudo apt-get install python3-tk
```

## Usage

### GUI (Recommended)

```bash
uv run gui.py
```

1. **Settings Tab**: Configure process name, paths, and backup settings
2. **Status Tab**: Monitor game status, view recent backups, check logs
3. Click **Start Monitor** to begin automatic backups

### CLI

```bash
uv run main.py
# OR
python main.py
```

Press `Ctrl+C` to stop.

## Configuration

### GUI Settings
- **Process Name**: Game process to monitor (e.g., "Silksong")
- **Original Save Path**: File or folder to back up
- **Backup Save Path**: Where to store backups
- **Check Interval**: Seconds between checks (default: 60)
- **Max Backups**: Maximum backup count (default: 100)

### Backup Structure
```
backups/
├── 2025-01-24_10-30-15/
│   └── user1.dat  (or folder)
├── 2025-01-24_10-31-15/
│   └── user1.dat
└── ...
```

## Requirements

- Python 3.6+
- `pgrep` command (usually pre-installed)
- Tkinter (for GUI)
- `uv` for package management (recommended)

## How It Works

1. Checks if specified game process is running
2. When game is detected, checks if save files have changed (hash comparison)
3. Creates timestamped backup only if changes detected
4. Removes oldest backups when limit exceeded
5. Continues monitoring until stopped

## File Structure

```
Auto_saver/
├── main.py          # CLI daemon
├── gui.py           # GUI application
├── monitor_core.py  # Shared monitoring logic
├── backups/         # Backup storage (gitignored)
└── README.md        # This file
```
