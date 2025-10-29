# Convert Auto Save Monitor to Web App

## Tech Stack (Modern & Future-Proof)

**Backend:**

* **Python 3.8+** - Core monitoring logic
* **FastAPI** - Modern async web framework (industry standard)
* **Uvicorn** - ASGI server (handles HTTP requests)
* **monitor_core.py** - Existing logic (no changes needed)

**Frontend:**

* **HTML5** - Structure
* **CSS3** - Modern styling
* **Vanilla JavaScript** - API calls and interactivity (no frameworks)

**API Style:**

* **GET** - For reading data (status, backups, logs)
* **POST** - For all actions (start, stop, update settings)
* **Simple RPC-style** - Clear endpoint names in URL paths

## Architecture Flow

```
User double-clicks run_web.py
    ↓
Uvicorn starts listening on localhost:8000
    ↓
Browser opens automatically
    ↓
User interacts with HTML/CSS/JS UI
    ↓
JavaScript → HTTP → Uvicorn → FastAPI → monitor_core.py
```

## API Endpoints (GET + POST Only)

### Read Operations (GET):

* `GET /` - Serve main HTML page
* `GET /api/status` - Get current status (game running, backup count, last backup)
* `GET /api/backups` - Get list of recent backups
* `GET /api/settings` - Get current settings
* `GET /api/logs` - Get recent activity logs

### Actions (POST):

* `POST /api/start` - Start monitoring
* `POST /api/stop` - Stop monitoring
* `POST /api/settings/update` - Update settings (interval, max backups, paths)
* `POST /api/logs/clear` - Clear activity logs

## Project Structure

```
Auto_saver/
├── run_web.py           # Double-click launcher
├── web_app.py           # FastAPI backend
├── monitor_core.py      # Existing monitoring logic (unchanged)
├── main.py              # CLI (keep for reference)
├── gui.py               # Old tkinter (keep for reference)
├── templates/
│   └── index.html       # Main web page (two tabs)
├── static/
│   ├── css/
│   │   └── style.css    # Modern styling
│   └── js/
│       └── app.js       # Fetch API calls
├── backups/             # Backup storage
├── requirements.txt     # Dependencies
└── README.md            # Updated instructions
```

## Implementation Steps

### 1. Backend (`web_app.py`)

* FastAPI app with GET/POST endpoints
* Uses `monitor_core.py` for monitoring
* Runs monitoring in background thread
* Serves static files (HTML/CSS/JS)
* Simple polling (frontend checks status every 2 seconds)

### 2. Frontend (HTML/CSS/JS)

* Two-tab interface (Status, Settings)
* JavaScript polls `/api/status` every 2 seconds
* Fetch API for all communication
* Clean, separated files

### 3. Launcher (`run_web.py`)

* Runs Uvicorn programmatically
* Waits for server startup
* Opens browser automatically

### 4. Dependencies (`requirements.txt`)

```
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
```

### 5. Update README

* Quick Start: "Double-click `run_web.py`"
* Remove tkinter warnings
* Add: `pip install -r requirements.txt`

## Benefits

* No tkinter crashes
* Works on all Python versions
* Modern, future-proof
* Simple GET/POST API
* Easy to maintain
* Browser-based

### To-dos

* [X] Update README with Quick Start instructions
