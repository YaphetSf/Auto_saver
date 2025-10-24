# Auto Save Monitor - TODO & Status

## ✅ Completed Features

- [x] Initialize git repository
- [x] Create Python virtual environment with uv
- [x] Create .gitignore for Python project
- [x] Implement process monitoring (pgrep for Silksong)
- [x] Implement backup function with timestamped folders
- [x] Implement FIFO management (max 100 backups)
- [x] Implement main daemon loop with 60s intervals
- [x] Add signal handling (SIGINT, SIGTERM) with immediate shutdown
- [x] Add file comparison (MD5 hash) to skip duplicate backups
- [x] Add configurable save file name (easy switch between user1/user2/user3)
- [x] Exclude backups/ directory in .gitignore
- [x] Clean logging output

## 📋 Current Configuration

**Default Settings (line 25 in main.py):**
```python
self.save_file_name = "user1.dat"  # Change to user1.dat, user2.dat, or user3.dat
```

**Save File Path (macOS):**
```
/Users/dingzhong/Library/Application Support/unity.Team-Cherry.Silksong/1018808405/
```

**Process Name:**
- Currently: "Silksong"

**Backup Settings:**
- Interval: 60 seconds
- Max backups: 100 (FIFO)
- Backup location: `./backups/YYYY-MM-DD_HH-MM-SS/`

## 🔄 How It Works

1. Daemon runs continuously in background
2. Checks every 60s if "Silksong" process is running (using pgrep)
3. When game detected, backs up save file every 60s
4. Compares save file to latest backup via MD5 hash
5. Only creates backup if file has changed (prevents duplicates)
6. Maintains max 100 backups using FIFO deletion
7. Press Ctrl+C to shutdown immediately

## 🚀 Usage

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the daemon
python main.py

# Stop the daemon
# Press Ctrl+C (shuts down immediately)
```

## 📝 Future Enhancements (Not Implemented Yet)

### High Priority
- [ ] Add Linux support (auto-detect OS and use correct save file paths)
- [ ] Add Windows support
- [ ] Add tkinter GUI for cross-platform interface
  - Status indicator (game running/not running)
  - Last backup timestamp
  - Backup count (X/100)
  - Start/Stop buttons
  - Settings panel (process name, save file, interval, max backups)
  - Backup browser with restore functionality
  - Manual "Backup Now" button

### Medium Priority
- [ ] Config file support (JSON/YAML) instead of hardcoded values
- [ ] Multiple game profiles (monitor multiple games)
- [ ] Backup compression to save disk space
- [ ] Backup notes/tags (manual save points)
- [ ] Restore functionality (copy backup back to save location)

### Low Priority
- [ ] System tray icon (platform-specific)
- [ ] Backup cloud sync (optional)
- [ ] Backup diff viewer (see what changed between saves)
- [ ] Export/import backup collections

## 🐧 Linux Support Notes

**For Linux, change line 27 to:**
```python
self.save_file_path = Path(f"~/.config/unity3d/Team-Cherry/Silksong/{self.save_file_name}").expanduser()
```

Or check these locations:
- `~/.config/unity3d/Team-Cherry/Silksong/`
- `~/.local/share/Team-Cherry/Silksong/`

## 🪟 Windows Support Notes

**For Windows, typical Unity save location:**
```
%APPDATA%\..\LocalLow\Team-Cherry\Silksong\
```

Process monitoring will need to change from `pgrep` to `tasklist` or `psutil` library.

## 📊 GUI Design (tkinter - Planned)

```
┌─────────────────────────────────┐
│  Auto Save Monitor          [_][□][×]│
├─────────────────────────────────┤
│                                 │
│  Status: ● Silksong Running     │
│  Last Backup: 2 minutes ago     │
│  Backups: 47 / 100              │
│                                 │
│  [Start Monitor] [Stop Monitor] │
│  [Backup Now]   [Open Folder]   │
│                                 │
├─ Settings ──────────────────────┤
│  Process Name: [Silksong     ]  │
│  Save File:    [user1.dat    ]  │
│  Interval (s): [60           ]  │
│  Max Backups:  [100          ]  │
│                                 │
│  [Save Settings]                │
│                                 │
├─ Recent Backups ────────────────┤
│  2025-10-24 15:42:30 (397KB)   │
│  2025-10-24 15:37:30 (406KB)   │
│  2025-10-24 15:32:30 (406KB)   │
│                                 │
└─────────────────────────────────┘
```

## 📁 Project Structure

```
Auto_saver/
├── main.py              # Main daemon script (205 lines)
├── README.md            # Documentation
├── TODO.md              # This file
├── .gitignore           # Git ignore rules
├── .venv/               # Virtual environment
└── backups/             # Backup storage (gitignored)
    ├── 2025-10-24_15-25-38/
    │   └── user3.dat
    ├── 2025-10-24_15-30-38/
    │   └── user3.dat
    └── ... (up to 100 folders)
```

## 🔧 Quick Tips

**To change save file:**
Edit line 25 in `main.py`:
```python
self.save_file_name = "user3.dat"  # Change to desired save file
```

**To compare two backups manually:**
```bash
# Check if files are different
diff backups/2025-10-24_15-37-30/user1.dat backups/2025-10-24_15-42-30/user1.dat

# Check file sizes and timestamps
ls -la backups/*/user1.dat

# Check MD5 hashes
md5 backups/*/user1.dat
```

---

Last Updated: 2024-10-24
Status: ✅ Core functionality complete, GUI planned for future

