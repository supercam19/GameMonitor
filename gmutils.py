import json
import os
import subprocess

import customtkinter
import requests
import win32api
import ctypes

from screeninfo import screeninfo


def json_read_safe(file, key):
    json_file = load_settings()
    if key in json_file:
        return json_file[key]


def json_read_safe_default(file, key, default):
    if json_read_safe(file, key):
        return json_read_safe(file, key)
    json_file = load_settings()
    json_file[key] = default
    save_settings(json_file)
    return default


def check_files():
    os.chdir(".")
    if not os.path.isfile("displayz.exe"):
        # print("displayz.exe not found, downloading...")
        url = "https://github.com/michidk/displayz/releases/download/0.1.0/displayz.exe"
        try:
            r = requests.get(url, allow_redirects=True)

            with open("displayz.exe", "wb") as f:
                f.write(r.content)
            # print("displayz.exe downloaded")
        except:
            pass
    if not os.path.isfile("settings.json"):
        with open("settings.json", "w") as f:
            f.write('{"default_monitor": 0, "games": []}')
    if not os.path.isfile("icon.ico"):
        url = "https://raw.githubusercontent.com/supercam19/GameMonitor/main/icon.ico"
        try:
            r = requests.get(url, allow_redirects=True)

            with open("icon.ico", "wb") as f:
                f.write(r.content)
        except:
            pass


def get_pid_from_name(process_name):
    try:
        output = subprocess.check_output(['tasklist', '/fi', f'imagename eq {process_name}', '/fo', 'csv']).decode(
            'utf-8').strip()
        lines = output.split('\n')
        if len(lines) > 1:
            # Assuming the first line is the header
            pid_str = lines[1].split(',')[1].strip().strip('"')  # Remove surrounding double quotes
            pid = int(pid_str)
            return pid
    except subprocess.CalledProcessError:
        pass
    return None


def save_settings(settings):
    with open("settings.json", "w") as f:
        json.dump(settings, f, indent=4)


def load_settings():
    with open("settings.json", "r") as f:
        return json.load(f)


def getFileProperties(fname):
    # https://stackoverflow.com/a/7993095
    # Altered to return only ProductName or file name if no ProductName
    """
    Read all properties of the given file return them as a dictionary.
    """
    propNames = ('Comments', 'InternalName', 'ProductName',
        'CompanyName', 'LegalCopyright', 'ProductVersion',
        'FileDescription', 'LegalTrademarks', 'PrivateBuild',
        'FileVersion', 'OriginalFilename', 'SpecialBuild')

    props = {'FixedFileInfo': None, 'StringFileInfo': None, 'FileVersion': None}

    try:
        # backslash as parm returns dictionary of numeric info corresponding to VS_FIXEDFILEINFO struc
        fixedInfo = win32api.GetFileVersionInfo(fname, '\\')
        props['FixedFileInfo'] = fixedInfo
        props['FileVersion'] = "%d.%d.%d.%d" % (fixedInfo['FileVersionMS'] / 65536,
                fixedInfo['FileVersionMS'] % 65536, fixedInfo['FileVersionLS'] / 65536,
                fixedInfo['FileVersionLS'] % 65536)

        # \VarFileInfo\Translation returns list of available (language, codepage)
        # pairs that can be used to retreive string info. We are using only the first pair.
        lang, codepage = win32api.GetFileVersionInfo(fname, '\\VarFileInfo\\Translation')[0]

        # any other must be of the form \StringfileInfo\%04X%04X\parm_name, middle
        # two are language/codepage pair returned from above

        strInfo = {}
        for propName in propNames:
            strInfoPath = u'\\StringFileInfo\\%04X%04X\\%s' % (lang, codepage, propName)
            ## print str_info
            strInfo[propName] = win32api.GetFileVersionInfo(fname, strInfoPath)

        props['StringFileInfo'] = strInfo
    except:
        return os.path.basename(fname).rstrip(".exe")
    if props.get("StringFileInfo").get("ProductName") is None:
        return os.path.basename(fname).rstrip(".exe")
    return props.get("StringFileInfo").get("ProductName")


def popup(title, message):
    ctypes.windll.user32.MessageBoxW(0, message, title, 0)

# might implement later
# def get_installed_games():
#     games = []
#     subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
#
#     try:
#         with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey) as key:
#             for i in range(winreg.QueryInfoKey(key)[0]):
#                 subkey_name = winreg.EnumKey(key, i)
#                 with winreg.OpenKey(key, subkey_name) as subkey:
#                     if subkey_name.startswith("Steam App"):
#                         try:
#                             display_name, _ = winreg.QueryValueEx(subkey, "InstallLocation")
#                             games.append(display_name)
#                         except FileNotFoundError:
#                             print("Could not find install location")  # Some entries may not have a DisplayName
#     except Exception as e:
#         print(f"Error: {e}")
#
#     return games


def reveal_monitor_ids(window):
    # so broken
    monitors = screeninfo.get_monitors()
    popups = []
    for monitor in monitors:
        popups.append(customtkinter.CTkToplevel(window))
        popups[-1].geometry(f"100x100+{monitor.x + 0.5*monitor.width - 50}+{monitor.y+ 0.5*monitor.height - 50}")
        popups[-1].attributes("-topmost", True)
        label = customtkinter.CTkLabel(popups[-1], text=f"Monitor ID: {len(popups) -1}", font=("Arial", 20))
        label.pack(pady=10, side="top")
        popups[-1].after(5000, popups[-1].destroy)
    return popups


