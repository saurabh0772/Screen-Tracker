# ScreenTracker 📸

**ScreenTracker** is a powerful and lightweight Python utility designed to quickly capture your entire screen and simultaneously log the names of all currently running applications.

It runs silently in the background and listens for a global hotkey, making it perfect for quickly logging your workspace state, auditing activity, or creating point-in-time snapshots of your work environment.

---

## 🌟 Features

- **Global Hotkey:** Listens for `Ctrl + Alt + Q` from anywhere in Windows, even when running in the background.
- **Full-Screen Capture:** Instantly takes a high-quality screenshot of all active monitors.
- **Smart App Logging:** Automatically lists clean, accurate names of all running applications, filtering out background noise and system processes.
- **Structured JSON Logging:** Saves metadata (timestamp, OS, username, screenshot path, and active apps) to a consolidated JSON file for easy parsing and tracking.
- **Professional Terminal Output:** Provides a clean, structured, and informative terminal UI for easy monitoring.

---

## 🛠️ Prerequisites

Before you begin, ensure you have met the following requirements:
- **Operating System:** Windows 10 / 11
- **Python Version:** Python 3.7 or higher

---

## 🚀 Installation

1. **Clone or download this repository:**
   ```bash
   git clone https://github.com/yourusername/ScreenTracker.git
   cd ScreenTracker
   ```

2. **(Optional but recommended) Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 💻 Usage

1. **Start the tracker from your terminal:**
   ```bash
   python screen_tracker.py
   ```
   *You will see a professional startup banner indicating the tool is active.*

2. **Trigger the capture:**
   While the script is running, press **`Ctrl + Alt + Q`** at any time to take a snapshot.

3. **Output Structure:**
   When triggered, the tool will:
   - Save a new screenshot in the `screenshot/` directory (e.g., `screenshot_20260630_120000.png`).
   - Update the `app_log.json` file in the `app_name/` directory with the new entry.
   - Display a beautifully formatted summary in your terminal.

4. **Stop the tracker:**
   Press `Ctrl + C` in the terminal to exit the application gracefully.

---

## 📂 Folder Structure

```
ScreenTracker/
│
├── screen_tracker.py     # Main application script
├── requirements.txt      # Python dependencies
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
        "OS": "Windows",
        "username": "User",
        "screenshot": "screenshot\\screenshot_20260630_114500.png",
        "applications": [
            "Antigravity IDE",
            "ChatGPT",
            "Command Prompt",
            "Google Chrome"
        ]
    }
]
```

---

## ⚙️ Troubleshooting

- **Hotkey Not Registering:** Ensure you are running the script with appropriate permissions (sometimes administrator privileges are required for global hotkeys on Windows).
- **Missing Dependencies:** Run `pip install -r requirements.txt` again to ensure `keyboard`, `pygetwindow`, and `Pillow` are installed.

---

## 📜 License

This project is open-source and available under the MIT License. 
