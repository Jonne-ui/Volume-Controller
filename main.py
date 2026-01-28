from __future__ import print_function
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
import keyboard
import json

volumeUp = "ctrl+å"
volumeDown = "ctrl+ä"

#Get audio sessions
sessions = AudioUtilities.GetAllSessions()

def readHotkeys():
    with open('hotkeys.json', 'r') as hotkeys:
        binds = json.load(hotkeys)
    print(binds["Spotify.exe"])

def getAppAudioStartLevel(appName):
     sessions = AudioUtilities.GetAllSessions()
     for session in sessions:
        volumeLevel = session._ctl.QueryInterface(ISimpleAudioVolume)
        if session.Process and session.Process.name() == appName:
            return volumeLevel.GetMasterVolume()

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

def increaseVolume():
    changeAppAudio("Spotify.exe", 0.05)

def decreaseVolume():
    changeAppAudio("Spotify.exe", -0.05)

keyboard.add_hotkey(volumeUp, increaseVolume)
keyboard.add_hotkey(volumeDown, decreaseVolume)
keyboard.wait()

readHotkeys()