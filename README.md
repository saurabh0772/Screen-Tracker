# ScreenTracker 📸

**ScreenTracker** is a powerful and lightweight Python utility designed to quickly capture your screen and simultaneously log the names of all currently running applications.

It runs in the background as a daemon and listens for a global hotkey, making it perfect for tracking your workspace state, auditing activity, or creating point-of-time snapshots of your work environment.

---

## 🌟 Features

- **Cross-Platform Global Hotkey Support**:
  - **Windows**: `Ctrl + Alt + Q`
  - **Linux / Xubuntu**: `Ctrl + Alt + Q`
  - **macOS**: `Cmd + I`
- **Full-Screen Capture**: Instantly takes a high-quality screenshot of all active monitors.
- **Smart App Logging**: Automatically lists clean, accurate names of all running applications, filtering out background noise and system processes.
- **Structured JSON Logging**: Saves metadata (timestamp, OS, username, screenshot path, and active apps) to a consolidated JSON file for easy parsing and tracking.
- **Professional Terminal Output**: Provides a clean, structured, and informative terminal UI for easy monitoring.

---

## 🛠️ Prerequisites

Before you begin, ensure you have met the following requirements:
- **Python Version**: Python 3.7 or higher
- **Operating Systems**:
  - **Windows 10 / 11**
  - **Linux (Ubuntu, Xubuntu, etc.)**: Supports both X11 and Wayland sessions.
  - **macOS**: High Sierra (10.13) or newer.

### Platform-Specific Setup

#### Linux / Xubuntu
Install `scrot` or `gnome-screenshot` so the script can capture the GUI layout cleanly:
```bash
sudo apt update && sudo apt install scrot
```

#### macOS
Ensure Python has **Accessibility Permissions** so it can register global hotkeys:
1. Open **System Settings** -> **Privacy & Security** -> **Accessibility**.
2. Add and check your Terminal application (e.g., Terminal, iTerm2, or VS Code) to grant it access.

---

## 🚀 Installation

1. **Clone or download this repository:**
   ```bash
   git clone https://github.com/yourusername/ScreenTracker.git
   cd ScreenTracker
   ```

2. **Create and activate a virtual environment:**
   - **Windows:**
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   - **Linux / macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: The requirements file uses standard environment markers to only install platform-relevant packages like `PyGetWindow` for Windows and `pynput` for Linux/macOS.)*

---

## 💻 Usage

### Daemon Mode (Background Listening)

1. **Start the background listener:**
   ```bash
   python screen_tracker.py
   ```

2. **Trigger the capture:**
   Minimize or use your active apps, and press the global hotkey at any time:
   - **Windows**: Press **`Ctrl + Alt + Q`**
   - **Linux / Xubuntu**: Press **`Ctrl + Alt + Q`**
   - **macOS**: Press **`Cmd + I`**

3. **Exit the daemon:**
   Press `Ctrl + C` in the terminal to exit gracefully.

---

### Ubuntu/Xubuntu Wayland Mode (Recommended Fallback)

On Wayland-based Linux sessions, security policies block background processes from globally listening to keystrokes. If the background daemon fails to capture hotkeys, we recommend using a system-level shortcut:

1. **Configure a system keyboard shortcut:**
   - Open **Settings** -> **Keyboard** -> **Application Shortcuts** (on Xubuntu) or **Keyboard Shortcuts** (on Ubuntu).
   - Click **Add** or **Add Shortcut** (`+`):
     - **Name / Command**: `/absolute/path/to/venv/bin/python3 /absolute/path/to/screen_tracker.py --trigger`
     - **Shortcut**: Press **`Ctrl + Alt + Q`**
2. **Use**: Press `Ctrl + Alt + Q` anytime. ScreenTracker will run, capture the screen/processes, update the log, and exit instantly.

---

## 📁 Output Structure

When triggered, the tool will:
- Save a new screenshot in the `screenshot/` directory (e.g., `screenshot/screenshot_20260630_120000.png`).
- Update the `app_log.json` file in the `app_name/` directory with the new entry.
- Display a beautifully formatted summary in your terminal.

```
ScreenTracker/
│
├── screen_tracker.py     # Main application script
├── requirements.txt      # Python dependencies (with OS-conditional installs)
├── README.md             # This documentation file
│
├── screenshot/           # Directory where all screenshots are saved
│   └── screenshot_YYYYMMDD_HHMMSS.png
│
└── app_name/             # Directory where the JSON logs are stored
    └── app_log.json      # Consolidated JSON log of all captures
```

---

## 📄 Example JSON Output

The `app_log.json` file keeps a chronological record of your captures:

```json
[
    {
        "timestamp": "2026-06-30 11:45:00",
        "OS": "Linux",
        "username": "saurabh",
        "screenshot": "screenshot/screenshot_20260630_114500.png",
        "applications": [
            "Visual Studio Code",
            "Brave Browser",
            "Terminal"
        ]
    },
    {
        "timestamp": "2026-06-30 12:05:00",
        "OS": "Darwin",
        "username": "macosuser",
        "screenshot": "screenshot/screenshot_20260630_120500.png",
        "applications": []
    }
]
```

---

## ⚙️ Troubleshooting

- **macOS Hotkey Not Registering**: Ensure your Terminal app is checked in **System Settings -> Privacy & Security -> Accessibility**. If it still doesn't work, restart the terminal.
- **Linux Wayland Hotkey Blocked**: If `pynput` complains or fails to detect keys, use the **Xubuntu Keyboard Application Shortcuts** method to trigger the script natively using the system window manager.
- **Missing CLI tools on Linux**: If screenshots fail to save, ensure `scrot` is installed: `sudo apt install scrot`.

---

## 📜 License

This project is open-source and available under the MIT License.
