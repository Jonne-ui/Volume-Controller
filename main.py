from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
import keyboard
import json
import sys
import pystray
import os
import winreg
from tkinter import *
from tkinter import ttk
from PIL import Image

appdataPath = os.getenv('APPDATA')
HOTKEYS_PATH = os.path.join(appdataPath, 'VolumeController', 'hotkeys.json')
STARTUP_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "VolumeController"

os.makedirs(os.path.join(appdataPath, 'VolumeController'), exist_ok=True)

if not os.path.exists(HOTKEYS_PATH):
    with open(HOTKEYS_PATH, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=4)


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

def is_startup_enabled():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY, 0, winreg.KEY_READ) as key:
            winreg.QueryValueEx(key, APP_NAME)
            return True
    except FileNotFoundError:
        return False

def enable_startup():
    exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY, 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, f'"{exe_path}"')

def disable_startup():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, APP_NAME)
    except FileNotFoundError:
        pass

def toggle_startup(icon, item):
    if is_startup_enabled():
        disable_startup()
    else:
        enable_startup()

def build_tray_menu():
    return pystray.Menu(
        pystray.MenuItem('Show', showApp, default=True),
        pystray.MenuItem(
            'Run at startup',
            toggle_startup,
            checked=lambda item: is_startup_enabled()
        ),
        pystray.MenuItem('Exit', exitApp)
    )

#Create window
WINDOW_WIDTH = 240

root = Tk()
root.title("Volume controller")
root.iconbitmap(resource_path("Images/favicon.ico"))
root.geometry("240x295")
root.resizable(False, False)


def minimizeToTray():
    root.withdraw()
    image = Image.open(resource_path("Images/favicon.ico"))
    icon = pystray.Icon("Name", image, "Volume controller", build_tray_menu())
    icon.run()

def exitApp(icon):
    icon.stop()
    root.destroy()

def showApp(icon):
    icon.stop()
    root.after(0, root.deiconify)


root.protocol("WM_DELETE_WINDOW", minimizeToTray)

#Get audio sessions
sessions = AudioUtilities.GetAllSessions()

def getAppAudioStartLevel(appName):
     sessions = AudioUtilities.GetAllSessions()
     for session in sessions:
        volumeLevel = session._ctl.QueryInterface(ISimpleAudioVolume)
        if session.Process and session.Process.name() == appName:
            return volumeLevel.GetMasterVolume()

#Change apps audio
def changeAppAudio(appName, volumeChange):
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process and session.Process.name() == appName:
            currentAppVol = session.SimpleAudioVolume
            appVol = currentAppVol.GetMasterVolume()
            newVol = appVol + volumeChange
            newVol = max(0.0, min(1.0, newVol))
            currentAppVol.SetMasterVolume(newVol, None)
            print(f'{appName}" volume: {currentAppVol.GetMasterVolume()}')

def increaseVolume(appName):
    changeAppAudio(appName, 0.05)

def decreaseVolume(appName):
    changeAppAudio(appName, -0.05)
     
def readHotkeys():
    with open(HOTKEYS_PATH, 'r') as hotkeys:
        binds = json.load(hotkeys)

    for app_name, actions in binds.items():
        for action, keybind in actions.items():
            if not keybind or keybind.strip() == "":
                continue
            if action == "VolumeUp":
                keyboard.add_hotkey(keybind, lambda a=app_name: increaseVolume(a))
            elif action == "VolumeDown":
                keyboard.add_hotkey(keybind, lambda a=app_name: decreaseVolume(a))

def resetHotkeyUp():
    reset_field_up()
    selectedApp = getSelectedApp()
    
    with open(HOTKEYS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if selectedApp in data:
        data[selectedApp]["VolumeUp"] = ""
    
    with open(HOTKEYS_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    reloadHotkeys()

def resetHotkeyDown():
    reset_field_down()
    selectedApp = getSelectedApp()
    
    with open(HOTKEYS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if selectedApp in data:
        data[selectedApp]["VolumeDown"] = ""
    
    with open(HOTKEYS_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    reloadHotkeys()

#Info Text
infoText = Label(root, text="Select an app to set Hotkey", font=('Segoe UI', 12, 'bold'))
infoText.grid(row=0, column=0, columnspan=2, padx=15, pady=5)

#Volume Up entry
volUpText = Label(root, text="Volume Up:", font=('Segoe UI', 12, 'bold'))
volUpText.grid(row=2, column=0)

hkEntry = Entry(root, width=24, cursor="arrow")
hkEntry.grid(row=3, column=0, padx=20, pady=5)

resetBtn = Button(root, text="↺", command=resetHotkeyUp)
resetBtn.grid(row=6, column=1, padx=(0, 25), pady=8)

#Volume Down entry
volDownText = Label(root, text="Volume Down:",font=('Segoe UI', 12, 'bold'))
volDownText.grid(row=4, column=0)

volDown = Entry(root, width=24, cursor="arrow")
volDown.grid(row=5, column=0, pady=5)

currentKeyBindUp = StringVar()
currentKeyBindDown = StringVar()

currentBindUp = Label(root, textvariable=currentKeyBindUp, justify='left', wraplength=WINDOW_WIDTH/2, font=('Segoe UI', 8))
currentBindUp.grid(row=6, column=0, sticky='w', padx=(17,0), pady=(5,0))
currentBindDown = Label(root, textvariable=currentKeyBindDown, justify='left', wraplength=WINDOW_WIDTH/2, font=('Segoe UI', 8))
currentBindDown.grid(row=7, column=0, sticky='w', padx=(17,0), pady=(5,0))

resetBtn2 = Button(root, text="↺", command=resetHotkeyDown)
resetBtn2.grid(row=7, column=1, padx=(0, 25), pady=8)

root.grid_columnconfigure(1, weight=1)

hotkeyUp = []
hotkeyDown = []

def normalize(key):
    return {
        "Control_L": "Ctrl",
        "Control_R": "Ctrl",
        "Shift_L": "Shift",
        "Shift_R": "Shift",
        "Alt_L": "Alt",
        "Alt_R": "Alt",
    }.get(key, key)

def reset_field_up():
    hotkeyUp.clear()
    hkEntry.delete(0, "end")

def reset_field_down():
    hotkeyDown.clear()
    volDown.delete(0, "end")

def reloadHotkeys():
    keyboard.unhook_all()
    readHotkeys()
    showCurrentHotkey()

def setHotkey(selectedApp):
    selectedHotkeyUp = hkEntry.get()
    selectedHotkeyDown = volDown.get()
    newHotkey = {selectedApp:{ 
        "VolumeUp": selectedHotkeyUp,
        "VolumeDown": selectedHotkeyDown
    }}

    with open(HOTKEYS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    data.update(newHotkey)

    with open(HOTKEYS_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    reloadHotkeys()

def showCurrentHotkey():
    selectedApp = getSelectedApp()
    
    with open(HOTKEYS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    appData = data.get(selectedApp, {"VolumeUp": "", "VolumeDown": ""})
    upKey = appData.get('VolumeUp', '')
    downKey = appData.get('VolumeDown', '')

    currentKeyBindUp.set(f'current keybind 🡅 : {upKey} ')
    currentKeyBindDown.set(f'current keybind 🡇 : {downKey} ')

def key_handler_up(event):
    if event.keysym in {"BackSpace", "Escape"}:
        reset_field_up()
        return "break"

    if len(hotkeyUp) >= 3:
        return "break"

    key = normalize(event.char) if event.char.strip() else normalize(event.keysym)

    try:
        key.encode('ascii')
    except UnicodeEncodeError:
        return "break"
    
    if key in hotkeyUp:
        return "break"

    if (key.isalnum() and key.isascii()) or key in {"Ctrl", "Shift", "Alt"}:
        hotkeyUp.append(key)
        hkEntry.delete(0, "end")
        hkEntry.insert("end", "+".join(hotkeyUp))
        setHotkey(getSelectedApp())

    return "break"

def key_handler_down(event):
    if event.keysym in {"BackSpace", "Escape"}:
        reset_field_down()
        return "break"

    if len(hotkeyDown) >= 3:
        return "break"

    key = normalize(event.char) if event.char.strip() else normalize(event.keysym)

    try:
        key.encode('ascii')
    except UnicodeEncodeError:
        return "break"

    if key in hotkeyDown:
        return "break"

    if (key.isalnum() and key.isascii()) or key in {"Ctrl", "Shift", "Alt"}:
        hotkeyDown.append(key)
        volDown.delete(0, "end")
        volDown.insert("end", "+".join(hotkeyDown))
        setHotkey(getSelectedApp())

    return "break"

hkEntry.bind("<Key>", key_handler_up)
volDown.bind("<Key>", key_handler_down)


#List all apps with audio and show selected app keybind
Apps = []
for session in sessions:
    if session.Process and session.Process.name():
        Apps.append(session.Process.name())
        opt = StringVar(value=session.Process.name())

openApps = ttk.Combobox(root, state='readonly', values=Apps)
openApps.bind("<<ComboboxSelected>>", lambda e: showCurrentHotkey())
openApps.current(0)
openApps.grid(row=1, column=0, pady=20)

#Get selected app
def getSelectedApp():
    selectedApp = openApps.get()
    return selectedApp

def takeFocus(event):
    if event.widget == root:
        root.focus_set()

root.bind("<Button-1>", takeFocus)

#Exit Keybind
root.bind("<Control-Alt-BackSpace>", sys.exit)

readHotkeys()
showCurrentHotkey()
root.mainloop()