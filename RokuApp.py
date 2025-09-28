import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread
from pynput import keyboard
from roku import Roku
import time
import ctypes

# --- Globals ---
capturing = False
selected_roku = None
devices = []
listener = None  # global listener


# --- Key mapping for keyboard control ---
KEYMAP = {
    'up': 'up',
    'down': 'down',
    'left': 'left',
    'right': 'right',
    'enter': 'select',
    'space': 'select',
    'backspace': 'back',
    'home': 'home',
    'p': 'play',
    's': 'stop',
    'r': 'rev',
    'f': 'fwd',
    'm': 'volumeMute',
}

# --- Discover Roku devices ---
def discover_devices():
    global devices
    try:
        devices = Roku.discover()
        if not devices:
            messagebox.showerror("Error", "No Roku devices found on the network.")
            return []
        return devices
    except Exception as e:
        messagebox.showerror("Error", f"Failed to discover Roku devices:\n{e}")
        return []

# --- Refresh device dropdown ---
def refresh_devices():
    global devices, selected_roku
    devices = discover_devices()
    device_names = [f"{dev.host}" for dev in devices]
    device_dropdown['values'] = device_names
    if devices:
        device_dropdown.current(0)
        selected_roku = devices[0]
        refresh_hdmi_inputs()
    else:
        selected_roku = None
        hdmi_dropdown['values'] = [""]

# --- Refresh HDMI inputs ---
def refresh_hdmi_inputs():
    global selected_roku
    if not selected_roku:
        hdmi_dropdown['values'] = [""]
        hdmi_dropdown.current(0)
        return
    try:
        hdmi_apps = [app.id for app in selected_roku.apps if app.id.startswith("tvinput.")]
        hdmi_dropdown['values'] = [""] + hdmi_apps
        hdmi_dropdown.current(0)
    except Exception as e:
        print(f"Failed to get HDMI inputs: {e}")
        hdmi_dropdown['values'] = [""]
        hdmi_dropdown.current(0)

# --- Keyboard listener ---
def on_press(key):
    global capturing, selected_roku
    if not capturing or not selected_roku:
        return
    try:
        if key == keyboard.Key.end:
            capturing = False
            status_var.set("Keyboard capture stopped.")
            return False

        key_str = None
        if hasattr(key, 'char') and key.char is not None:
            key_str = key.char.lower()
        elif hasattr(key, 'name'):
            key_str = key.name.lower()

        if key_str in KEYMAP:
            command = KEYMAP[key_str]
            try:
                getattr(selected_roku, command)()
                status_var.set(f"Sent '{command}' to {selected_roku.host}")
            except Exception as cmd_error:
                status_var.set(f"Failed '{command}': {cmd_error}")
    except Exception as e:
        print("Error handling key press:", e)

def toggle_capture():
    global capturing, listener
    if not selected_roku:
        messagebox.showwarning("Warning", "Please select a Roku device first.")
        return

    if capturing:
        # Stop capturing
        capturing = False
        if listener is not None:
            listener.stop()
            listener = None
        status_var.set(f"Keyboard capture stopped for {selected_roku.host}")
        root.after(0, update_capture_button)  # <-- thread-safe
    else:
        # Start capturing
        capturing = True
        status_var.set(f"Capturing keyboard input for {selected_roku.host} (Press END or click button to stop)")
        root.after(0, update_capture_button)  # <-- thread-safe
        if listener is None:
            listener = keyboard.Listener(on_press=on_press)
            listener.start()


def update_capture_button():
    if capturing:
        start_button.config(text="Stop Capturing Keyboard")
    else:
        start_button.config(text="Start Capturing Keyboard")


# --- Wake TV function ---
def wake_tv():
    global selected_roku
    if not selected_roku:
        messagebox.showwarning("Warning", "Please select a Roku device first.")
        return

    def _wake():
        try:
            for attempt in range(3):
                getattr(selected_roku, 'up')()
                time.sleep(0.5)

            hdmi_app_id = hdmi_var.get()
            if hdmi_app_id:
                try:
                    selected_roku.launch(hdmi_app_id)
                except Exception as e:
                    print(f"Failed to switch input: {e}")

            status_var.set("Wake TV command sent!")
        except Exception as e:
            print(f"Error in _wake: {e}")

    Thread(target=_wake).start()

# --- Print installed apps ---
def print_installed_apps():
    global selected_roku
    if not selected_roku:
        messagebox.showwarning("Warning", "Please select a Roku device first.")
        return
    try:
        print(f"Installed apps on Roku {selected_roku.host}:")
        for app in selected_roku.apps:
            print(f"App ID: {app.id}, Name: {app.name}, Version: {app.version}")
        status_var.set("Installed apps printed to console.")
    except Exception as e:
        print(f"Failed to get installed apps: {e}")

# --- Idle detection ---
class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint),
                ("dwTime", ctypes.c_uint)]

def get_idle_duration():
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
    millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
    return millis / 1000.0

def idle_wake_loop():
    idle_threshold = 300
    last_state_idle = True
    time.sleep(5)  # Give the user/system some time before checking
    while True:
        idle = get_idle_duration() > idle_threshold
        if last_state_idle and not idle:
            wake_tv()
        last_state_idle = idle
        time.sleep(2)

# --- GUI Setup ---
root = tk.Tk()
root.title("Roku Keyboard Remote")
root.geometry("650x300")
root.resizable(False, False)

# Styles
style = ttk.Style()
style.configure("TLabel", font=("Segoe UI", 10))
style.configure("TButton", font=("Segoe UI", 10), padding=6)
style.configure("TCombobox", padding=4)

# Device selection
device_frame = ttk.Frame(root, padding=15)
device_frame.pack(fill='x')
ttk.Label(device_frame, text="Select Roku Device:").pack(anchor='w')
device_dropdown = ttk.Combobox(device_frame, state="readonly")
device_dropdown.pack(fill='x', pady=5)
#device_dropdown.bind("<<ComboboxSelected>>", on_device_select)

# HDMI input selection
ttk.Label(device_frame, text="HDMI Input on Wake (optional):").pack(anchor='w', pady=(10,0))
hdmi_var = tk.StringVar()
hdmi_dropdown = ttk.Combobox(device_frame, textvariable=hdmi_var, state="readonly")
hdmi_dropdown['values'] = [""]
hdmi_dropdown.current(0)
hdmi_dropdown.pack(fill='x', pady=5)

# Buttons
button_frame = ttk.Frame(root, padding=10)
button_frame.pack(fill='x')
start_button = ttk.Button(button_frame, text="Start Capturing Keyboard", command=lambda: Thread(target=toggle_capture).start())
start_button.grid(row=0, column=0, padx=5, pady=5)
rescan_button = ttk.Button(button_frame, text="Rescan Devices", command=refresh_devices)
rescan_button.grid(row=0, column=1, padx=5, pady=5)
wake_button = ttk.Button(button_frame, text="Wake TV", command=wake_tv)
wake_button.grid(row=0, column=2, padx=5, pady=5)
apps_button = ttk.Button(button_frame, text="Get Installed Apps (console)", command=print_installed_apps)
apps_button.grid(row=0, column=3, padx=5, pady=5)

# Status bar
status_var = tk.StringVar()
status_var.set("Ready")
status_label = ttk.Label(root, textvariable=status_var, relief="sunken", anchor='w', padding=5)
status_label.pack(side='bottom', fill='x')

# Initial scan
refresh_devices()

# Idle detection
Thread(target=idle_wake_loop, daemon=True).start()

root.mainloop()
