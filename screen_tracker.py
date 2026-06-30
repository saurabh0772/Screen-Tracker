import platform
import os
import json
import getpass
import shutil
import time
import subprocess
import sys
from datetime import datetime
from PIL import ImageGrab

# Conditional imports based on OS
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_MAC = platform.system() == "Darwin"

if IS_WINDOWS:
    import keyboard
    # pyrefly: ignore [missing-import]
    import pygetwindow as gw
else:
    # On Linux, import keyboard (requires root), and pynput (non-root fallback)
    try:
        import keyboard
    except ImportError:
        keyboard = None
    try:
        from pynput import keyboard as pynput_keyboard
    except ImportError:
        pynput_keyboard = None

def print_banner(is_trigger_mode=False):
    banner = """
    ========================================================
                 S C R E E N   T R A C K E R
    ========================================================
    """
    print(banner)
    print(f"[*] System OS: {platform.system()} {platform.release()}")
    # Use SUDO_USER if available to display original user instead of 'root'
    current_user = os.environ.get("SUDO_USER", getpass.getuser())
    print(f"[*] User: {current_user}")
    print(f"[*] Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("--------------------------------------------------------")
    if is_trigger_mode:
        print("[+] Mode  : Single Capture (Triggered)")
    else:
        print("[+] Status: Active")
        hotkey_desc = "Cmd + I" if platform.system() == "Darwin" else "Ctrl + Alt + Q"
        print(f"[+] Hotkey: {hotkey_desc} (Press to capture)")
        print("[+] Exit  : Ctrl + C")
    print("========================================================\n")

def adjust_ownership(path):
    """Changes the owner of the path to the original SUDO_USER if running as root on Linux."""
    original_user = os.environ.get("SUDO_USER")
    if original_user and hasattr(os, "chown"):
        try:
            import pwd
            user_info = pwd.getpwnam(original_user)
            uid = user_info.pw_uid
            gid = user_info.pw_gid
            os.chown(path, uid, gid)
        except Exception:
            pass

def capture_screenshot(output_path):
    """Captures screenshot using scrot, gnome-screenshot, or PIL.ImageGrab as fallback.
    Handles root privilege environments by running GUI utilities under the original user session."""
    if IS_LINUX:
        original_user = os.environ.get("SUDO_USER")
        if original_user:
            # Run scrot as the GUI user to preserve X11/Wayland authorization
            try:
                res = subprocess.run(
                    ["sudo", "-u", original_user, "scrot", output_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                if res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    return True
            except Exception:
                pass

            # Try gnome-screenshot as the GUI user
            try:
                res = subprocess.run(
                    ["sudo", "-u", original_user, "gnome-screenshot", "-f", output_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                if res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    return True
            except Exception:
                pass

        # Fallback to direct run if not run via sudo or if above failed
        try:
            res = subprocess.run(["scrot", output_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                return True
        except Exception:
            pass

        try:
            res = subprocess.run(["gnome-screenshot", "-f", output_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                return True
        except Exception:
            pass

    # Default fallback (or Windows)
    try:
        img = ImageGrab.grab(all_screens=True)
        img.save(output_path)
        return True
    except Exception:
        pass
        
    return False

def get_linux_desktop_entries():
    """Parses .desktop files to map executable names to user-friendly app names."""
    app_map = {}
    search_dirs = ["/usr/share/applications", os.path.expanduser("~/.local/share/applications")]
    for d in search_dirs:
        if not os.path.exists(d):
            continue
        try:
            for filename in os.listdir(d):
                if not filename.endswith(".desktop"):
                    continue
                path = os.path.join(d, filename)
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        name, exec_name = None, None
                        in_desktop_entry = False
                        no_display = False
                        for line in f:
                            line = line.strip()
                            if line == "[Desktop Entry]":
                                in_desktop_entry = True
                            elif line.startswith("[") and line.endswith("]"):
                                in_desktop_entry = False
                            if in_desktop_entry:
                                if line.lower().startswith("nodisplay=") and "true" in line.lower():
                                    no_display = True
                                elif line.startswith("Name=") and not name:
                                    name = line.split("=", 1)[1].strip()
                                elif line.startswith("Exec=") and not exec_name:
                                    exec_val = line.split("=", 1)[1].strip()
                                    tokens = exec_val.split()
                                    if tokens:
                                        exec_path = tokens[0].replace('"', '').replace("'", "")
                                        exec_name = os.path.basename(exec_path)
                        # Only map names if it's a visible application (not NoDisplay=true)
                        if name and exec_name and not no_display:
                            app_map[exec_name] = name
                            for suffix in ["-stable", "-browser"]:
                                if exec_name.endswith(suffix):
                                    app_map[exec_name[:-len(suffix)]] = name
                except Exception:
                    continue
        except Exception:
            continue
    return app_map

def get_linux_visible_window_titles():
    """Returns titles of currently visible X11 windows using xdotool when available."""
    if not shutil.which("xdotool"):
        return []

    try:
        res = subprocess.run(
            ["xdotool", "search", "--onlyvisible", "--name", ""],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if res.returncode != 0:
            return []

        titles = []
        for window_id in res.stdout.splitlines():
            window_id = window_id.strip()
            if not window_id:
                continue
            try:
                title_res = subprocess.run(
                    ["xdotool", "getwindowname", window_id],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False,
                )
            except Exception:
                continue

            title = (title_res.stdout or "").strip()
            if not title:
                continue

            normalized = title.strip()
            if normalized.lower() in {
                "desktop",
                "panel",
                "xfce4-panel",
                "xfce4-screensaver",
                "xfwm4",
            }:
                continue
            titles.append(normalized)
        return titles
    except Exception:
        return []


def normalize_app_name_from_title(title):
    """Converts a window title into a user-friendly application name."""
    title = (title or "").strip()
    if not title:
        return ""

    lower_title = title.lower()
    if "visual studio code" in lower_title:
        return "Visual Studio Code"
    if "google chrome" in lower_title or "chrome" in lower_title:
        return "Google Chrome"
    if "firefox" in lower_title:
        return "Firefox"
    if "terminal" in lower_title:
        return "Terminal"
    if "bulk rename" in lower_title:
        return "Bulk Rename"

    if " - " in title:
        parts = [part.strip() for part in title.split(" - ") if part.strip()]
        if len(parts) >= 2:
            candidate = parts[-1].strip()
            if candidate.lower() not in {"panel", "terminal"}:
                return candidate

    return title


def get_running_apps():
    """Extracts running applications based on OS."""
    if IS_WINDOWS:
        titles = gw.getAllTitles()
        app_names = set()
        ignored_titles = {"Program Manager", "Windows Input Experience", "Taskbar"}

        for title in titles:
            title = title.strip()
            if not title or title in ignored_titles:
                continue

            app_name = title
            if " - " in title:
                parts = title.split(" - ")
                app_name = parts[-1].strip()
                if app_name.endswith((".py", ".txt", ".md")) and len(parts) >= 2:
                    app_name = parts[-2].strip()

            lower_title = title.lower()
            if "screenshot with app names" in lower_title or "chatgpt" in lower_title:
                app_name = "ChatGPT"
            elif "antigravity ide" in lower_title:
                app_name = "Antigravity IDE"

            app_names.add(app_name)
        return sorted(app_names)

    elif IS_LINUX:
        window_titles = get_linux_visible_window_titles()
        if window_titles:
            app_names = {
                normalize_app_name_from_title(title)
                for title in window_titles
                if normalize_app_name_from_title(title)
            }
            if app_names:
                return sorted(app_names)

        # Fallback to /proc-based process detection only when no visible windows were found.
        proc_names = set()
        try:
            for pid in os.listdir("/proc"):
                if pid.isdigit():
                    try:
                        with open(os.path.join("/proc", pid, "cmdline"), "r") as f:
                            cmdline = f.read().split("\x00")

                        if cmdline and cmdline[0]:
                            cmd_str = " ".join(cmdline)
                            exec_path = cmdline[0]
                            base = os.path.basename(exec_path)

                            is_background = False
                            if "--gapplication-service" in cmd_str:
                                is_background = True
                            elif exec_path.startswith("/usr/libexec/"):
                                is_background = True
                            elif any(term in exec_path for term in ["evolution-data-server", "goa-daemon", "gnome-keyring", "ibus-"]):
                                is_background = True

                            if not is_background and base:
                                proc_names.add(base)

                                with open(os.path.join("/proc", pid, "comm"), "r") as comm_f:
                                    comm = comm_f.read().strip()
                                    if comm:
                                        proc_names.add(comm)
                    except (IOError, OSError):
                        continue
        except Exception:
            pass

        desktop_map = get_linux_desktop_entries()
        fallback_map = {
            "chrome": "Google Chrome",
            "chrome-stable": "Google Chrome",
            "google-chrome": "Google Chrome",
            "firefox": "Firefox",
            "firefox-bin": "Firefox",
            "code": "Visual Studio Code",
            "cursor": "Cursor",
            "brave": "Brave Browser",
            "brave-browser": "Brave Browser",
            "antigravity-ide": "Antigravity IDE",
            "slack": "Slack",
            "discord": "Discord",
            "spotify": "Spotify",
            "gnome-terminal": "Terminal",
            "bash": "Terminal",
            "zsh": "Terminal",
            "python3": "Python Application",
            "python": "Python Application",
        }

        app_names = set()
        for p in proc_names:
            p_lower = p.lower()
            if p_lower in fallback_map:
                app_names.add(fallback_map[p_lower])
            elif p in desktop_map:
                app_names.add(desktop_map[p])
            elif p_lower in desktop_map:
                app_names.add(desktop_map[p_lower])
            elif "antigravity" in p_lower:
                app_names.add("Antigravity IDE")

        ignored_names = {
            "bash", "sh", "systemd", "dbus", "gnome-shell", "Python Application",
            "Xwayland", "gjs", "at-spi2-registryd", "at-spi-bus-launcher",
            "dconf-service", "gvfsd", "goa-daemon", "evolution-alarm-notify"
        }
        filtered_names = {app for app in app_names if app not in ignored_names}
        if not filtered_names:
            filtered_names = app_names

        return sorted(filtered_names)

    return []

def take_screenshot_and_print():
    try:
        ts_now = datetime.now()
        ts = ts_now.strftime("%Y%m%d_%H%M%S")
        clean_ts = ts_now.strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n[{clean_ts}] >> CAPTURE EVENT TRIGGERED <<")
        print("-" * 56)

        # 1. Take Screenshot
        save_dir = "screenshot"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            adjust_ownership(save_dir)
            print(f"[*] Created directory: {save_dir}/")
            
        temp_file = os.path.join(save_dir, f"screenshot_{ts}.png")
        success = capture_screenshot(temp_file)
        if success:
            adjust_ownership(temp_file)
            print(f"[+] Screenshot saved : {temp_file}")
        else:
            print("[!] Failed to capture screenshot.")
        
        # 2. Extract running applications
        app_list = get_running_apps()
        
        # 3. Save JSON log
        app_save_dir = "app_name"
        if not os.path.exists(app_save_dir):
            os.makedirs(app_save_dir)
            adjust_ownership(app_save_dir)
            print(f"[*] Created directory: {app_save_dir}/")
            
        json_file = os.path.join(app_save_dir, "app_log.json")
        
        entry = {
            "timestamp": clean_ts,
            "OS": platform.system(),
            "username": os.environ.get("SUDO_USER", getpass.getuser()),
            "screenshot": temp_file,
            "applications": app_list
        }
        
        data = []
        if os.path.exists(json_file):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                data = []
                
        data.append(entry)
        
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        
        adjust_ownership(json_file)
            
        print(f"[+] Log file updated : {json_file}")
        print("-" * 56)
        
        # 4. Print running applications
        print("--- Running Applications ---")
        for app in app_list:
            print(f"  - {app}")
        print("========================================================\n")
            
    except Exception as e:
        print(f"[!] Error during capture: {e}")

def run_daemon():
    print_banner(is_trigger_mode=False)
    
    if IS_WINDOWS:
        keyboard.add_hotkey("ctrl+alt+q", take_screenshot_and_print)
        print("[*] Daemon listening... Press Ctrl+C to exit.")
        keyboard.wait()
    else:
        # Linux / macOS daemon mode
        is_root = os.geteuid() == 0 if hasattr(os, "geteuid") else False
        
        if not IS_MAC and is_root and keyboard is not None:
            print("[*] Running as root. Listening globally system-wide using 'keyboard' library...")
            keyboard.add_hotkey("ctrl+alt+q", take_screenshot_and_print)
            print("[*] Daemon listening... Press Ctrl+C to exit.")
            keyboard.wait()
        elif pynput_keyboard is not None:
            print(f"[*] Running on {'macOS' if IS_MAC else 'Linux'}. Listening using 'pynput' library...")
            if IS_LINUX:
                print("[!] Note: On Wayland sessions, global keyboard hooks might only capture events when X11/XWayland windows are active.")
                print("[!] Recommended: Run as root (sudo) or use system shortcuts to bind 'python3 screen_tracker.py --trigger' to Ctrl+Alt+Q.")
            print("-" * 56)
            
            def on_activate():
                take_screenshot_and_print()
                
            hotkey_def = '<cmd>+i' if IS_MAC else '<ctrl>+<alt>+q'
            try:
                listener = pynput_keyboard.GlobalHotKeys({
                    hotkey_def: on_activate
                })
                listener.start()
                print(f"[*] Daemon listening on {hotkey_def}... Press Ctrl+C to exit.")
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n[+] Exiting gracefully...")
            except Exception as e:
                print(f"[!] pynput listener error: {e}")
                if IS_MAC:
                    print("[*] Make sure the terminal app has Accessibility permission in System Settings -> Privacy & Security -> Accessibility.")
                else:
                    print("[*] Please run as root (sudo) or use the --trigger option with a system-wide hotkey.")
        else:
            print("[!] Error: No suitable keyboard library available for background listening.")
            if IS_MAC:
                print("[*] Please run: pip install pynput")
            else:
                print("[*] Please run as root: sudo ./venv/bin/python3 screen_tracker.py")
                print("[*] OR recommended: Use system keyboard shortcuts to run 'python3 screen_tracker.py --trigger'")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--trigger", "-t"):
        print_banner(is_trigger_mode=True)
        take_screenshot_and_print()
    else:
        run_daemon()