import keyboard

ToggleKeyUp = "ctrl+å"
ToggleKeyDown = "ctrl+ä"


KeyPressed = None

import keyboard

keyboard.on_press_key("p", lambda _:print("You pressed p"))



audio = 0.0

def changeAudio():
    global audio
    audio += 0.1
    print(audio)

keyboard.add_hotkey(ToggleKeyUp, changeAudio)

keyboard.wait()