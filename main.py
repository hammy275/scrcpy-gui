"""
Copyright 2019 hammy3502

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from subprocess import call

try:
    import PySimpleGUI as sg
except ModuleNotFoundError:
    print("PySimpleGUI not installed! Please run python3 -m pip install PySimpleGUI before starting this program!")
    exit(1)

"""
TODO:
Custom port option when Wi-Fi selected
"""

print("Launching GUI...")
layout = [
    [sg.Text("Leave your phone unplugged or unplug it now!")],
    [sg.Text("Mode: "), sg.Radio("USB", "mode", default=True, enable_events=True, key="usb_mode"), sg.Radio("Wi-Fi", "mode", enable_events=True, key="wifi_mode")],
    [sg.Text("IP Address: "), sg.InputText(key='addr', disabled=True, size=(20,None))],
    [sg.Checkbox("Custom resolution: ", key="use_resolution", enable_events=True), sg.InputText(key='resolution',size=(8,None),disabled=True)],
    [sg.Checkbox("Custom bitrate: ", key="use_bitrate", enable_events=True), sg.InputText(key='bitrate',size=(4,None),disabled=True)],
    [sg.Checkbox("Device serial number: ", key="use_sn", enable_events=True), sg.InputText(key='sn',size=(32,None),disabled=True)],
    [sg.Checkbox("Fullscreen mode: ", key="use_fullscreen"), sg.Checkbox("Show physical screen taps: ", key="use_touches")],
    [sg.Button("Start scrcpy"), sg.Button("Exit")]
    ]

window = sg.Window('scrcpy GUI', layout=layout)

cancel = False #Used later to check if we should exit after breaking out of the loop
while True:
    event, values = window.Read()
    if event in (None, 'Exit'): #None if we're closing, Exit if exit button is pressed
        cancel = True
        break
    if event == "Start scrcpy":
        break
    if values["wifi_mode"] == True:
        window.Element('addr').Update(disabled=False)
        window.Element('sn').Update(disabled=True)
        window.Element('use_sn').Update(disabled=True) #Allow entering of IP address, and disable use of serial number checking
    else:
        window.Element('addr').Update(disabled=True)
        window.Element('sn').Update(disabled=not(values["use_sn"]))
        window.Element('use_sn').Update(disabled=False) #Disable entering of IP address, and enable use of serial number checking
    if event == "use_resolution":
        window.Element("resolution").Update(disabled=not(values["use_resolution"]))
    elif event == "use_bitrate":
        window.Element("bitrate").Update(disabled=not(values["use_bitrate"]))
    elif event == "use_sn":
        window.Element("sn").Update(disabled=not(values["use_sn"])) #User must check box for option before being allowed to input said option
if cancel: #Window closed or exit button pressed
    print("Exiting...")
    exit(0)

print("Closing window...") #Close window while starting scrcpy
window.Close()

print("Killing ADB server...") #Kill any previous ADB servers, just in case.
call(["adb", "kill-server"])

sg.Popup("Plug in your phone, then click Ok!")

if values["wifi_mode"]:
    print("Wi-Fi preparation.")
    if values['addr'] == '':
        sg.Popup("IP address not specified!")
        exit(1)
    else:
        call(["adb", "shell", "exit"])
        connect_to = str(values["addr"] + ":5555") #Custom port may go here at some point
        call(["adb", "tcpip", "5555"]) #Custom port may go here at some point
        call(["adb", "connect", connect_to])
        sg.Popup("Unplug your phone, then click Ok!")


command = ["scrcpy"]
print("Running scrcpy command...")

if values["use_resolution"] and values["resolution"] != "":
    command.append("-m " + values["resolution"])
if values["use_bitrate"] and values["bitrate"] != "":
    command.append("-b " + values["bitrate"])
if values["usb_mode"] and values["use_sn"] and values["sn"] != "":
    command.append("-s " + values["sn"])
if values["use_fullscreen"]:
    command.append("-f")
if values["use_touches"]:
    command.append("-t") #Assemble command
print("Running command: " + " ".join(command))
exit(call(command)) #Run scrcpy command and give the exit code scrcpy gives us