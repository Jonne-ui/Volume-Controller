from __future__ import print_function
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
import keyboard
import json
import sys
import time
from tkinter import *
from tkinter import ttk

#Create window
root = Tk()
root.title("Volume controller")
root.geometry("520x280")

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
            print(f"volume: {currentAppVol.GetMasterVolume()}")

def increaseVolume(appName):
    changeAppAudio(appName, 0.05)

def decreaseVolume(appName):
    changeAppAudio(appName, -0.05)
     
def readHotkeys():
    with open('hotkeys.json', 'r') as hotkeys:
        binds = json.load(hotkeys)
        print(binds)

    for app_name, actions in binds.items():
        for action, keybind in actions.items():
            if action == "VolumeUp":
                keyboard.add_hotkey(keybind, lambda: increaseVolume(app_name))
            
            if action == "VolumeDown":
                keyboard.add_hotkey(keybind, lambda: decreaseVolume(app_name))
            print(action, keybind, app_name)

#Info Text
infoText = Label(root, text="Select an app to set Hotkey", font='Helvetica 14 bold')
infoText.grid(row=0, column=0, padx=20, pady=5)

#Get active List item
hkEntry = Entry(root, width=30, cursor="arrow")
hkEntry.grid(row=1, column=1)

hotkey = []

def normalize(key):
    return {
        "Control_L": "Ctrl",
        "Control_R": "Ctrl",
        "Shift_L": "Shift",
        "Shift_R": "Shift",
        "Alt_L": "Alt",
        "Alt_R": "Alt",
    }.get(key, key)

def reset_field():
    hotkey.clear()
    hkEntry.delete(0, "end")

def key_handler(event):
    # BACKSPACE = reset
    if event.keysym in {"BackSpace", "Escape"}:
        reset_field()
        return "break"

    if len(hotkey) >= 3:
        return "break"

    key = normalize(event.keysym)

    if key in hotkey:
        return "break"

    # allow modifiers or one normal key
    if key.isalnum() or key in {"Ctrl", "Shift", "Alt"}:
        hotkey.append(key)
        hkEntry.delete(0, "end")
        hkEntry.insert("end", "+".join(hotkey))
        print(hotkey)

    return "break"

hkEntry.bind("<Key>", key_handler)

#Set hotkey in hotkeys.json
#  "!!!!!!fix utf-8!!!!!!"
def setHotkey():
    selectedHotkey = hkEntry.get()
    print(selectedHotkey)

#Get selected app
def getSelectedApp():
    selectedApp = openApps.get()
    if selectedApp != "Select an app":
        print(selectedApp)
        setHotkey()

#List all apps with audio
Apps = []
for session in sessions:
    if session.Process and session.Process.name():
        Apps.append(session.Process.name())
        opt = StringVar(value=session.Process.name())

openApps = ttk.Combobox(root, state='readonly', values=Apps)
openApps.set("Select an app")
openApps.grid(row=1, column=0, pady=20)

applyBtn = Button(root, text="Apply", font='Helvetica 14 bold', relief='solid', command=getSelectedApp)
applyBtn.grid(row=0, column=1, pady=20)


#Exit Keybind
root.bind("<Control-Alt-BackSpace>", sys.exit)

readHotkeys()

root.mainloop()