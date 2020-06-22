#!/usr/bin/python3
"""
Copyright 2020 hammy3502

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
import platform
import json
from time import sleep

class CommandExecutionError(Exception):
    pass


def full(file_name):
    """Full Path.

    Converts ~'s, .'s, and ..'s to their full paths (~ to /home/username)

    Args:
        file_name (str): Path to convert

    Returns:
        str: Converted path

    """
    return os.path.abspath(os.path.expanduser(file_name))


def get_db():
    """Get Database.

    Returns:
        dict: Database. {} if database fails to be read or found on disk.

    """
    try:
        with open(full("./scrcpy-gui-settings.json")) as f:
            db = json.load(f)
            print("Successfully loaded database!")
    except FileNotFoundError:
        db = {}
        print("Couldn't find database file! Defaulting to empty database...")
    except json.decoder.JSONDecodeError:
        db = {}
        print("Failed decoding database! Defaulting to new database...")
    return db


def pip_install(package):
    """Install PIP Package.

    Args:
        package (str): Package(s) from pip to install

    """
    try:
        run([sys.executable, "-m", "pip", "install", package])
    except CommandExecutionError:
        msg = "Failed to install {}! Leaving scrcpy-gui...".format(package)
        try:
            sg.Popup(msg)
        except NameError:
            print(msg)
        except tkinter.TclError:
            print(msg)
        sys.exit(1)


def apt_install(package):
    """Install apt Package.

    Args:
        package (str): Package(s) from apt to install

    """
    try:
        run(["sudo", "apt", "install", package, "-y"])
    except CommandExecutionError:
        msg = "Failed to install {}! Leaving scrcpy-gui...".format(package)
        try:
            sg.Popup(msg)
        except NameError:
            print(msg)
        except tkinter.TclError:
            print(msg)
        sys.exit(1)


def get_val(key, default):
    """Get DB Value.

    Args:
        key (str): Key to get
        default (any): Value to return if key doesn't exist

    Returns:
        any: Value at key in db.

    """
    try:
        return db[key]
    except KeyError:
        return default


def write_db():
    """Write Database to File."""
    try:
        with open(full("./scrcpy-gui-settings.json"), "w") as dbf:
            json.dump(db, dbf)
        print("Database written!")
    except FileNotFoundError:
        print(json.dumps(db))
        print("Database failed to be written and is dumped to screen!")


db = get_db()
is_crostini = os.path.isfile("/usr/share/themes/CrosAdapta/index.theme")

try:
    import tkinter
except ImportError:
    print("tkinter not installed, please install it! This can be done with 'sudo apt install python3-tk' on Debian based systems!")
    sys.exit(1)

try:
    import PySimpleGUI as sg
except ImportError:
    pysgui_install = input("PySimpleGUI not installed! Would you like to install it [Y/n]?")
    if pysgui_install.lower() == "y" or pysgui_install.lower() == "yes" or pysgui_install.lower() == "":
        pip_install("PySimpleGUI")
        import PySimpleGUI as sg
    else:
        sys.exit(1)

def run(cmd_list):
    """Run Command."""
    err = call(cmd_list)
    if err != 0:
        raise CommandExecutionError("Error running {}".format(" ".join(cmd_list)))


def scrcpy_install_linux():
    """Setup scrcpy and adb on Linux."""
    if os.getuid() != 0:
        sg.Popup("Root is required to complete this first time setup! Please run this script as root!")
        sys.exit(1)
    else:
        print("Creating progress window")
        bar_layout = [
            [sg.Text("Preparing scrcpy and adb...")],
            [sg.ProgressBar(100, orientation='h', size=(20, 20), key='installbar')]
        ]
        install_window = sg.Window("Installing...", bar_layout)
        bar = install_window.FindElement("installbar")
        install_window.Read(timeout=0)
        print("Installing scrcpy and ADB...")
        bar.UpdateBar(2)
        try:
            import distro
        except ImportError:
            if sg.PopupYesNo("The 'distro' package isn't installed! Would you like scrcpy-gui to install it?") == "Yes":
                pip_install("distro")
                import distro
            else:
                sys.exit(1)
        dist = distro.linux_distribution(full_distribution_name=False)
        ###ADB###
        bar.UpdateBar(10)
        if which("apt") is not None:
            print("Installing ADB through apt")
            run(["sudo", "apt", "update"])
            bar.UpdateBar(30)
            run(["sudo", "apt", "install", "adb", "-y"])
        elif which("apt-get") is not None:
            print("Installing ADB through apt-get")
            run(["sudo", "apt-get", "update"])
            bar.UpdateBar(30)
            run(["sudo", "apt", "install", "adb", "-y"])
        elif which("pacman") is not None:
            print("Installing ADB through pacman")
            run(["sudo", "pacman", "-Syu"])
            bar.UpdateBar(30)
            run(["sudo", "pacman", "-S", "android-tools"])
        elif which("yum") is not None:
            print("Installing ADB through yum")
            run(["yum", "install", "android-tools"])
        else:
            pass  # Use compile from source below
        bar.UpdateBar(60)
        ###SCRCPY###
        if which("pacman") is not None:
            print("Installing scrcpy through pacman")
            run(["sudo", "pacman", "-S", "scrcpy"])
        else:
            if which("apt") is not None:
                print("Compiling and installing scrcpy from source!")
                print("Installing requirements through apt!")
                apt_install("git")
                bar.UpdateBar(63)
                print("Compiling and installing scrcpy")
                os.chdir("/tmp/")
                try:
                    rmtree("/tmp/scrcpy-gui-setup")
                except FileNotFoundError:
                    pass
                os.mkdir("/tmp/scrcpy-gui-setup")
                os.chdir("/tmp/scrcpy-gui-setup/")
                ecode = call(["git", "clone", "--branch", "v1.14", "https://github.com/Genymobile/scrcpy.git"])
                if ecode != 0:
                    print("Error getting source code! Please check the error log above! Exiting setup...")
                    sys.exit(1)
                bar.UpdateBar(65)
                print("Getting compile dependencies...")
                apt_install("ffmpeg libsdl2-2.0-0")
                bar.UpdateBar(70)
                apt_install("gcc git pkg-config meson ninja-build")
                bar.UpdateBar(75)
                apt_install("libavcodec-dev libavformat-dev libavutil-dev")
                bar.UpdateBar(80)
                apt_install("libsdl2-dev")
                bar.UpdateBar(82)
                os.chdir("/tmp/scrcpy-gui-setup/scrcpy")
                print("Getting pre-built server binary")
                ecode = call(["wget", "https://github.com/Genymobile/scrcpy/releases/download/v1.14/scrcpy-server-v1.14"])
                if ecode != 0:
                    print("Error getting server JAR! Please see the error above! Exiting...")
                    sys.exit(1)
                os.rename("scrcpy-server-v1.14", "server.jar")
                bar.UpdateBar(88)
                print("Compiling...")
                ecode = call(["meson", "x", "--buildtype", "release", "--strip", "-Db_lto=true", "-Dprebuilt_server=/tmp/scrcpy-gui-setup/scrcpy/server.jar"])
                if ecode != 0:
                    print("Error while compiling! Exiting...")
                    sys.exit(1)
                bar.UpdateBar(93)
                ecode = call(["ninja", "-Cx"])
                if ecode != 0:
                    print("Error while compiling! Exiting...")
                    sys.exit(1)
                bar.UpdateBar(97)
                ecode = call(["sudo", "ninja", "-Cx", "install"])
                if ecode != 0:
                    print("Error while installing! Exiting...")
                    sys.exit(1)
            else:
                sg.Popup("Your OS doesn't support automatic installation of scrcpy.")
                sys.exit(1)
        bar.UpdateBar(100)
        sg.Popup("Please run this script again as your user (not root!).")
        sys.exit(0)


def scrcpy_install_win():
    """Setup scrcpy and adb on Windows."""
    print("Creating progress window")
    bar_layout = [
        [sg.Text("Preparing scrcpy and adb...")],
        [sg.ProgressBar(100, orientation='h', size=(20, 20), key='installbar')]
    ]
    install_window = sg.Window("Installing...", bar_layout)
    bar = install_window.FindElement("installbar")
    install_window.Read(timeout=0)
    print("Installing scrcpy and ADB...")
    os.chdir(full("%temp%"))
    bar.UpdateBar(1)
    print("Removing old scrcpy-gui-setup folder (if it exists!).")
    try:
        rmtree("scrcpy-gui-setup")
    except FileNotFoundError:
        pass
    bar.UpdateBar(2)
    os.mkdir("scrcpy-gui-setup")
    is_64bits = sys.maxsize > 2**32
    os.chdir(full("%temp%/scrcpy-gui-setup"))
    try:
        import requests
    except ImportError:
        print("Requests module isn't installed!")
        install = sg.PopupYesNo("requests isn't installed! Would you like to install it?")
        if install == "Yes":
            pip_install("requests")
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
    scrcpy_install = full("%userprofile%/scrcpy")
    print("Extracting ZIP to {}".format(scrcpy_install))
    try:
        import zipfile
    except ImportError:
        print("zipfile module isn't installed!")
        sg.Popup("zipfile module is not installed! Please install it!")
        sys.exit(1)
    print("Deleting old scrcpy install area (if it exists!)")
    with zipfile.ZipFile("scrcpy.zip", "r") as z_file:
        try:
            rmtree(full(scrcpy_install))
        except FileNotFoundError:
            pass
        bar.UpdateBar(65)
        print("Doing ZIP extract...")
        os.mkdir(scrcpy_install)
        os.chdir(scrcpy_install)
        z_file.extractall(full(scrcpy_install))
        bar.UpdateBar(100)


if (which("adb") == None or which("scrcpy") == None) and not(os.path.isfile(full("%userprofile%/scrcpy/scrcpy.exe"))):
    print("ADB/scrcpy not installed!")
    osys = platform.system()
    auto_install_prompt = "Would you like to automatically install ADB and scrcpy? By doing so, you agree to any and all license agreements that come with those pieces of software!"
    if osys == "Windows":
        response = sg.PopupYesNo(auto_install_prompt)
        if response == "Yes":
            scrcpy_install_win()
        else:
            print("Not installing! Exiting...")
            sys.exit(1)
    elif osys == "Linux":
        try:
            response = sg.PopupYesNo(auto_install_prompt)
        except tkinter.TclError:
            if is_crostini:
                print("#"*20)
                print("Please run the following command: xhost +si:localuser:root")
                print("#"*20)
            sys.exit(1)
        if response == "Yes":
            scrcpy_install_linux()
        else:
            print("Not installing! Exiting...")
            sys.exit(1)
    else:
        print("Your OS does not support automatic installation! Exiting...")
        sg.Popup("ADB not installed! Please install ADB (comes with scrcpy on Windows), and add it to your PATH!")
        sys.exit(1)


print("Building GUI...")
rotation_options = {
    "Natural orientation": "0",
    "90 degrees counterclockwise": "1",
    "180 degrees": "2",
    "90 degrees clockwise": "3"
}
layout = [
    [sg.Text("Select options:")],
    [sg.Text("Mode: "), sg.Radio("USB", "mode", default=get_val("is_usb", True), enable_events=True, key="usb_mode"), sg.Radio("Wi-Fi", "mode", enable_events=True, key="wifi_mode", default=not(get_val("is_usb", True)))],
    [sg.Text("IP Address: "), sg.InputText(key='addr', default_text=get_val("addr", ""), disabled=get_val("is_usb", True), size=(20,None))],
    [sg.Checkbox("Custom port: ", key="use_port", default=get_val("use_port", False), enable_events=True, disabled=not(get_val("is_usb", True))), sg.InputText(key='port',size=(8,None),disabled=not(get_val("use_port", False)))],
    [sg.Checkbox("Custom resolution: ", key="use_resolution", enable_events=True, default=get_val("use_resolution", False)), sg.InputText(key='resolution',size=(8,None), disabled=not(get_val("use_resolution", False)), default_text=get_val("resolution", ""))],
    [sg.Checkbox("Custom bitrate: ", key="use_bitrate", enable_events=True, default=get_val("use_bitrate", False)), sg.InputText(key='bitrate',size=(4,None),disabled=not(get_val("use_bitrate", False)), default_text=get_val("bitrate", ""))],
    [sg.Checkbox("Device serial number: ", key="use_sn", enable_events=True, default=get_val("use_sn", False)), sg.InputText(key='sn',size=(32,None),disabled=not(get_val("use_sn", False)), default_text=get_val("sn", ""))],
    [sg.Checkbox("Set maximum framerate: ", key="use_framerate", enable_events=True, default=get_val("use_framerate", False)), sg.InputText(key='framerate',size=(4,None), disabled=not(get_val("use_framerate", True)), default_text=get_val("framerate", ""))],
    [sg.Checkbox("Set Orientation: ", key="set_orien", enable_events=True, default=get_val("set_orien", False)), sg.Combo(list(rotation_options.keys()), key="orien", disabled=not(get_val("set_orien", True)), default_value=get_val("orien", ""))],
    [sg.Checkbox("Fullscreen mode", key="use_fullscreen", default=get_val("full", False)), sg.Checkbox("Show physical screen taps", key="use_touches", default=get_val("taps", False))],
    [sg.Checkbox("Turn screen off on start", key="sleep_screen", enable_events=True, default=get_val("sleep", False)), sg.Checkbox("Keep scrcpy window on top", key="on_top", default=get_val("top", False))],
    [sg.Checkbox("Disable device control", key="no_device_control", enable_events=True, default=get_val("no_control", False)), sg.Checkbox("Keep device awake", key="keep_awake", enable_events=True, default=get_val("keep_awake", False))],
    [sg.Text("If there is an option to allow USB debugging, please allow it now!")],
    [sg.Button("Start scrcpy"), sg.Button("Exit")]
    ]

print("Launching GUI...")
try:
    window = sg.Window('scrcpy GUI', layout=layout)
except tkinter.TclError:
    if is_crostini:
        print("#"*20)
        print("Please run the following command: xhost +si:localuser:root")
        print("#"*20)
    sys.exit(1)

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
        window.Element('use_port').Update(disabled=False)
        window.Element('port').Update(disabled=not(values['use_port']))
        window.Element('sn').Update(disabled=True)
        window.Element('use_sn').Update(disabled=True) #Allow entering of IP address and port, and disable use of serial number checking
    else:
        window.Element('addr').Update(disabled=True)
        window.Element('use_port').Update(disabled=True)
        window.Element('port').Update(disabled=True)
        window.Element('sn').Update(disabled=not(values["use_sn"]))
        window.Element('use_sn').Update(disabled=False) #Disable entering of IP address and port, and enable use of serial number checking
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

db = {
    "is_usb": values["usb_mode"],
    "addr": values["addr"],
    "use_port": values["use_port"],
    "port": values["port"],
    "use_resolution": values["use_resolution"], 
    "resolution": values["resolution"],
    "use_bitrate": values["use_bitrate"], 
    "bitrate": values["bitrate"],
    "use_sn": values["use_sn"], 
    "sn": values["sn"],
    "full": values["use_fullscreen"], "taps": values["use_touches"],
    "sleep": values["sleep_screen"], "top": values["on_top"],
    "no_control": values["no_device_control"],
    "use_framerate": values["use_framerate"], "framerate": values["framerate"],
    "set_orien": values["set_orien"], "orien": values["orien"],
    "keep_awake": values["keep_awake"]
}
write_db()

if cancel: #Window closed or exit button pressed
    print("Exiting...")
    sys.exit(0)

print("Closing window...") #Close window while starting scrcpy
window.Close()

if not(which("adb") != None and which("scrcpy") != None):
    full("%userprofile%/scrcpy/")
    print("Using scrcpy directory installed by scrcpy-gui!")

print("Killing ADB server...") #Kill any previous ADB servers, just in case.
run(["adb", "kill-server"])

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
        if values['use_port'] and values['port'] != "":
            try:
                port = int(values['port'])
                if port < 0 or port > 65536:
                    sg.Popup("Port must be between 0 and 65536!")
                    sys.exit(1)
                port = str(port)
            except ValueError:
                sg.Popup("Port must be a number!")
                sys.exit(1)
        else:
            port = "5555"
        run(["adb", "shell", "exit"])
        bar.UpdateBar(10)
        connect_to = str(values["addr"] + ":{}".format(port)) 
        bar.UpdateBar(20)
        run(["adb", "tcpip", port])
        bar.UpdateBar(30)
        sleep(2) #Waiting here can help things a decent amount of times
        bar.UpdateBar(35)
        run(["adb", "connect", connect_to])
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
if values["use_framerate"] and values["framerate"] != "":
    try:
        command.append("--max-fps " + str(int(values["framerate"])))  # Conversion makes sure we have a number
    except ValueError:
        print("Skipping framerate max because it isn't a number!")
if values["use_fullscreen"]:
    command.append("-f")
if values["set_orien"]:
    command.append("--lock-video-orientation " + rotation_options[values["orien"]])
if values["use_touches"]:
    command.append("-t") 
if values["no_device_control"]:
    command.append("-n")
if values["sleep_screen"]:
    command.append("-S")
if values["on_top"]:
    command.append("-T")
if values["keep_awake"]:
    command.append("-w") #Assemble command
bar.UpdateBar(100)
print("Running command: " + " ".join(command))
sys.exit(os.system(" ".join(command)) / 256) #Run scrcpy command and give the exit code scrcpy gives us