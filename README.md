# Auto Save Game Monitor

A Python daemon that automatically monitors for the Silksong game process and backs up save files every 60 seconds while the game is running.

## Features

- **Process Monitoring**: Uses `pgrep` to detect when Silksong is running
- **Automatic Backups**: Creates timestamped backups every 60 seconds while game is active
- **FIFO Management**: Maintains maximum of 100 backups, removing oldest when limit is reached
- **Graceful Shutdown**: Handles Ctrl+C and system signals properly
- **Cross-platform Ready**: Uses `pathlib.Path` for future Linux support

## Usage

### Running the Daemon

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the daemon
python main.py
```

### Stopping the Daemon

Press `Ctrl+C` to gracefully shutdown the daemon.

## Backup Structure

```
backups/
├── 2025-01-24_10-30-15/
│   └── user3.dat
├── 2025-01-24_10-31-15/
│   └── user3.dat
└── ... (up to 100 folders)
```

## Configuration

The daemon is configured with these hardcoded values:

- **Save File Path**: `/Users/dingzhong/Library/Application Support/unity.Team-Cherry.Silksong/1018808405/user3.dat`
- **Backup Directory**: `./backups/`
- **Check Interval**: 60 seconds
- **Max Backups**: 100 (FIFO deletion)

## Requirements

- Python 3.6+
- macOS (uses `pgrep` command)
- Save file must exist at the specified path

## Behavior

1. **Game Not Running**: Checks every 60 seconds for Silksong process
2. **Game Detected**: Starts backup mode, creates backup every 60 seconds
3. **Game Stopped**: Returns to monitoring mode
4. **Backup Limit**: Automatically removes oldest backups when exceeding 100

## Logging

The daemon provides console output showing:
- Startup information
- Game detection/stopping events
- Backup creation confirmations
- FIFO cleanup notifications
- Error messages
