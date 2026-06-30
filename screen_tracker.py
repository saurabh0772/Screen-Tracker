import keyboard
# pyrefly: ignore [missing-import]
import pygetwindow as gw
from PIL import ImageGrab
from datetime import datetime
import os
import json
import platform
import getpass
import time

def print_banner():
    banner = """
    ========================================================
                 S C R E E N   T R A C K E R
    ========================================================
    """
    print(banner)
    print(f"[*] System OS: {platform.system()} {platform.release()}")
    print(f"[*] User: {getpass.getuser()}")
    print(f"[*] Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("--------------------------------------------------------")
    print("[+] Status: Active")
    print("[+] Hotkey: Ctrl + Alt + Q (Press to capture)")
    print("[+] Exit  : Ctrl + C")
    print("========================================================\n")

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
            print(f"[*] Created directory: {save_dir}/")
            
        temp_file = os.path.join(save_dir, f"screenshot_{ts}.png")
        img = ImageGrab.grab(all_screens=True)
        img.save(temp_file)
        print(f"[+] Screenshot saved : {temp_file}")
        
        # 2. Extract running applications
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
        
        app_list = sorted(app_names)
        
        # 3. Save JSON log
        app_save_dir = "app_name"
        if not os.path.exists(app_save_dir):
            os.makedirs(app_save_dir)
            print(f"[*] Created directory: {app_save_dir}/")
            
        json_file = os.path.join(app_save_dir, "app_log.json")
        
        entry = {
            "timestamp": clean_ts,
            "OS": platform.system(),
            "username": getpass.getuser(),
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
            
        print(f"[+] Log file updated : {json_file}")
        print("-" * 56)
        
        # 4. Print running applications
        print("--- Running Applications ---")
        for app in app_list:
            print(f"  - {app}")
        print("========================================================\n")
            
    except Exception as e:
        print(f"[!] Error during capture: {e}")

if __name__ == "__main__":
    print_banner()
    keyboard.add_hotkey("ctrl+alt+q", take_screenshot_and_print)
    keyboard.wait()