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
from shutil import which,rmtree
import sys
import os
from platform import system
from time import sleep

try:
    import PySimpleGUI as sg
except ModuleNotFoundError:
    print("PySimpleGUI not installed! Please run python3 -m pip install PySimpleGUI before starting this program!")
    sys.exit(1)

def scrcpy_install_linux():
    print("Checking for root...")
    if os.getuid() != 0:
        sg.Popup("Root is required to complete this first time setup! Please run this script as root!")
        sys.exit(1)
    else:
        print("Creating progress window")
        bar_layout = [
            [sg.Text("Preparing scrcpy and adb...")],
            [sg.ProgressBar(100, orientation='h', size=(20, 20), key='installbar')]
        ]
        try:
            import distro
        except ModuleNotFoundError:
            sg.Popup("Please install distro with the command python3 -m pip install distro!")
            sys.exit(1)
        install_window = sg.Window("Installing...", bar_layout)
        bar = install_window.FindElement("installbar")
        install_window.Read(timeout=0)
        print("Installing scrcpy and ADB...")
        bar.UpdateBar(1)
        dist = distro.linux_distribution(full_distribution_name=False)
        bar.UpdateBar(3)
        dist = ["xubuntu", 1, 2]
        if dist[0] in ["linuxmint"] or "ubuntu" in dist[0]:
            print("Detected Ubuntu-based system!")
            print("Installing scrcpy through snap")
            bar.UpdateBar(50)
            os.system("snap install scrcpy")
            bar.UpdateBar(100)
            sg.Popup("Install complete! Please run scrcpy-gui as your intended user (usually not root).")
            sys.exit(0)
        else:
            sg.Popup("Distro does not support automatic install! Please manually install adb and scrcpy!")
            sys.exit(1)


def scrcpy_install_win():
    print("Creating progress window")
    bar_layout = [
        [sg.Text("Preparing scrcpy and adb...")],
        [sg.ProgressBar(100, orientation='h', size=(20, 20), key='installbar')]
    ]
    install_window = sg.Window("Installing...", bar_layout)
    bar = install_window.FindElement("installbar")
    install_window.Read(timeout=0)
    print("Installing scrcpy and ADB...")
    os.chdir(os.path.expandvars("%temp%"))
    bar.UpdateBar(1)
    print("Removing old scrcpy-gui-setup folder (if it exists!).")
    try:
        rmtree("scrcpy-gui-setup")
    except FileNotFoundError:
        pass
    bar.UpdateBar(2)
    os.mkdir("scrcpy-gui-setup")
    is_64bits = sys.maxsize > 2**32
    os.chdir(os.path.expandvars("%temp%/scrcpy-gui-setup"))
    try:
        import requests
    except ModuleNotFoundError:
        print("Requests module isn't installed!")
        sg.Popup("requests isn't installed! Please run python -m pip install PySimpleGUI before starting this program!")
        sys.exit(1)
    bar.UpdateBar(3)
    print("Downloading scrcpy zip...")
    if is_64bits:
        print("Choosing 64-bit version")
        f = requests.get("https://github.com/Genymobile/scrcpy/releases/download/v1.10/scrcpy-win64-v1.10.zip")
    else:
        print("Choosing 32-bit version.")
        f = requests.get("https://github.com/Genymobile/scrcpy/releases/download/v1.10/scrcpy-win32-v1.10.zip")
    bar.UpdateBar(4)
    open("scrcpy.zip", "wb").write(f.content)
    bar.UpdateBar(60)
    scrcpy_install = os.path.expandvars("%userprofile%/scrcpy")
    print("Extracting ZIP to {}".format(scrcpy_install))
    try:
        import zipfile
    except ModuleNotFoundError:
        print("zipfile module isn't installed!")
        sg.Popup("zipfile module is not installed! Please install it!")
        sys.exit(1)
    print("Deleting old scrcpy install area (if it exists!)")
    with zipfile.ZipFile("scrcpy.zip", "r") as z_file:
        try:
            rmtree(os.path.expandvars(scrcpy_install))
        except FileNotFoundError:
            pass
        bar.UpdateBar(65)
        print("Doing ZIP extract...")
        os.mkdir(scrcpy_install)
        os.chdir(scrcpy_install)
        z_file.extractall(os.path.expandvars(scrcpy_install))
        bar.UpdateBar(100)

if (which("adb") == None or which("scrcpy") == None) and not(os.path.isfile(os.path.expandvars("%userprofile%/scrcpy/scrcpy.exe"))):
    print("ADB/scrcpy not installed!")
    osys = system()
    if osys == "Windows":
        response = sg.PopupYesNo("Would you like to automatically install ADB and scrcpy? By doing so, you agree to any and all license agreements that come with those pieces of software!")
        if response == "Yes":
            scrcpy_install_win()
        else:
            print("Not installing! Exiting...")
            sys.exit(1)
    elif osys == "Linux":
        response = sg.PopupYesNo("Would you like to automatically install ADB and scrcpy? By doing so, you agree to any and all license agreements that come with those pieces of software!")
        if response == "Yes":
            scrcpy_install_linux()
        else:
            print("Not installing! Exiting...")
            sys.exit(1)
    else:
        print("OS does not support automatic installation! Exiting...")
        sg.Popup("ADB not installed! Please install ADB (comes with scrcpy on Windows), and add it to your PATH!")
        sys.exit(1)

print("Launching GUI...")
layout = [
    [sg.Text("Leave your phone unplugged or unplug it now!")],
    [sg.Text("Mode: "), sg.Radio("USB", "mode", default=True, enable_events=True, key="usb_mode"), sg.Radio("Wi-Fi", "mode", enable_events=True, key="wifi_mode")],
    [sg.Text("IP Address: "), sg.InputText(key='addr', disabled=True, size=(20,None))],
    [sg.Checkbox("Custom resolution: ", key="use_resolution", enable_events=True), sg.InputText(key='resolution',size=(8,None),disabled=True)],
    [sg.Checkbox("Custom bitrate: ", key="use_bitrate", enable_events=True), sg.InputText(key='bitrate',size=(4,None),disabled=True)],
    [sg.Checkbox("Device serial number: ", key="use_sn", enable_events=True), sg.InputText(key='sn',size=(32,None),disabled=True)],
    [sg.Checkbox("Fullscreen mode: ", key="use_fullscreen"), sg.Checkbox("Show physical screen taps: ", key="use_touches")],
    [sg.Checkbox("Turn screen off on start: ", key="sleep_screen", enable_events=True), sg.Checkbox("Keep scrcpy window on top: ", key="on_top")],
    [sg.Checkbox("Disable device control: ", key="no_device_control", enable_events=True)],
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
    elif event == "no_device_control":
        window.Element("sleep_screen").Update(disabled=values["no_device_control"])
    elif event == "sleep_screen":
        window.Element("no_device_control").Update(disabled=values["sleep_screen"])
    elif event == "use_sn":
        window.Element("sn").Update(disabled=not(values["use_sn"])) #User must check box for option before being allowed to input said option
if cancel: #Window closed or exit button pressed
    print("Exiting...")
    sys.exit(0)

print("Closing window...") #Close window while starting scrcpy
window.Close()

if not(which("adb") != None and which("scrcpy") != None):
    os.chdir(os.path.expandvars("%userprofile%/scrcpy/"))
    print("Using scrcpy directory installed by scrcpy-gui!")

print("Killing ADB server...") #Kill any previous ADB servers, just in case.
call(["adb", "kill-server"])

sg.Popup("Plug in your phone, then click Ok!")
adb_layout = [
    [sg.Text("Connecting to phone and launching scrcpy...")],
    [sg.ProgressBar(100, orientation='h', size=(20, 20), key='adbbar')]
]
adb_window = sg.Window("Launching...", adb_layout)
bar = adb_window.FindElement("adbbar")
adb_window.Read(timeout=0)
if values["wifi_mode"]:
    print("Wi-Fi preparation.")
    if values['addr'] == '':
        sg.Popup("IP address not specified!")
        sys.exit(1)
    else:
        call(["adb", "shell", "exit"])
        bar.UpdateBar(10)
        connect_to = str(values["addr"] + ":5555") #Custom port may go here at some point
        bar.UpdateBar(20)
        call(["adb", "tcpip", "5555"]) #Custom port may go here at some point
        bar.UpdateBar(30)
        sleep(2) #Waiting here can help things a decent amount of times
        bar.UpdateBar(35)
        call(["adb", "connect", connect_to])
        bar.UpdateBar(45)
        sg.Popup("Unplug your phone, then click Ok!")


command = ["scrcpy"]
print("Running scrcpy command...")
bar.UpdateBar(46)

if values["use_resolution"] and values["resolution"] != "":
    command.append("-m " + values["resolution"])
if values["use_bitrate"] and values["bitrate"] != "":
    command.append("-b " + values["bitrate"])
if values["usb_mode"] and values["use_sn"] and values["sn"] != "":
    command.append("-s " + values["sn"])
if values["use_fullscreen"]:
    command.append("-f")
if values["use_touches"]:
    command.append("-t") 
if values["no_device_control"]:
    command.append("-n")
if values["sleep_screen"]:
    command.append("-S")
if values["on_top"]:
    command.append("-T") #Assemble command
bar.UpdateBar(100)
print("Running command: " + " ".join(command))
sys.exit(call(command)) #Run scrcpy command and give the exit code scrcpy gives us