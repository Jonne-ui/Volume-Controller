from __future__ import print_function
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
import keyboard
import json
import sys
import pystray
import os
from tkinter import *
from tkinter import ttk
from PIL import Image

appdataPath = os.getenv('APPDATA')
HOTKEYS_PATH = os.path.join(appdataPath, 'VolumeController', 'hotkeys.json')

os.makedirs(os.path.join(appdataPath, 'VolumeController'), exist_ok=True)

if not os.path.exists(HOTKEYS_PATH):
    with open(HOTKEYS_PATH, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=4)


#Create window
WINDOW_WIDTH = 240

root = Tk()
root.title("Volume controller")
img = PhotoImage(file="Images/ico.png")
root.iconphoto(True, img)
root.geometry("240x295")
root.resizable(False, False)

def minimizeToTray():
    root.withdraw()
    image = Image.open("Images/favicon.ico")
    menu = (pystray.MenuItem('Show', showApp),
            pystray.MenuItem('Exit', exitApp)
            )
    icon = pystray.Icon("Name", image, "Volume controller", menu)
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

#Set hotkey in hotkeys.json
#  "!!!!!!fix utf-8!!!!!!"
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
    #print("Added:", newHotkey.keys())
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
    # BACKSPACE = reset
    if event.keysym in {"BackSpace", "Escape"}:
        reset_field_up()
        return "break"

    if len(hotkeyUp) >= 3:
        return "break"

    key = normalize(event.keysym)

    if key in hotkeyUp:
        return "break"

    # allow modifiers or one normal key
    if key.isalnum() or key in {"Ctrl", "Shift", "Alt"}:
        hotkeyUp.append(key)
        hkEntry.delete(0, "end")
        hkEntry.insert("end", "+".join(hotkeyUp))
        #print(hotkeyUp)
        setHotkey(getSelectedApp())

    return "break"

def key_handler_down(event):
    # BACKSPACE = reset
    if event.keysym in {"BackSpace", "Escape"}:
        reset_field_down()
        return "break"

    if len(hotkeyDown) >= 3:
        return "break"

    key = normalize(event.keysym)

    if key in hotkeyDown:
        return "break"

    # allow modifiers or one normal key
    if key.isalnum() or key in {"Ctrl", "Shift", "Alt"}:
        hotkeyDown.append(key)
        volDown.delete(0, "end")
        volDown.insert("end", "+".join(hotkeyDown))
        #print(hotkeyDown)
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
#openApps.set("Select an app")
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