import json
import os
import subprocess

import customtkinter
import requests
import win32api
import ctypes
from PIL import Image
import icoextract

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


def get_monitor_id_from_name(name):
    monitors = screeninfo.get_monitors()
    for i, monitor in enumerate(monitors):
        if monitor.name == name:
            return i

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

    # Generic `Product Name`'s that should be ignored and use the executable name instead
    # If you know of more generic ones, please add!
    ignore_generic = ("BootstrapPackagedGame")

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
    p_name = props.get("StringFileInfo").get("ProductName")
    if p_name is None or p_name in ignore_generic:
        return os.path.basename(fname).rstrip(".exe")
    return p_name


def icon_from_exe(exe, size=(32, 32)):
    return customtkinter.CTkImage(Image.open(icoextract.IconExtractor(exe).get_icon()).resize(size))


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


class MonitorPreview(customtkinter.CTkToplevel):
    def __init__(self, window):
        super().__init__(window)
        self.window = window

        self.monitors = screeninfo.get_monitors()
        self.title("Monitor Preview")



        left_bounds = [monitor.x for monitor in self.monitors]
        right_bounds = [monitor.x + monitor.width for monitor in self.monitors]
        top_bounds = [monitor.y for monitor in self.monitors]
        bottom_bounds = [monitor.y + monitor.height for monitor in self.monitors]

        bounding_width = max(right_bounds) - min(left_bounds)
        bounding_height = max(bottom_bounds) - min(top_bounds)
        x_offset = -min(left_bounds)
        y_offset = -min(top_bounds)
        scale = 0.2
        bounding_width *= scale
        bounding_height *= scale

        self.canvas = customtkinter.CTkCanvas(self, width=bounding_width, height=bounding_height, bg="gray")
        self.canvas.pack(fill="both", expand=True)

        self.geometry(f"+%d+%d" % (self.winfo_screenwidth() / 2 - bounding_width/2, self.winfo_screenheight() / 2 - bounding_height/2))
        print(f"{self.winfo_screenwidth() / 2 - bounding_width/2}+{self.winfo_screenheight() / 2 - bounding_height/2}")

        for monitor in self.monitors:
            self.canvas.create_rectangle(monitor.x + x_offset, monitor.y + y_offset, monitor.x + monitor.width + x_offset, monitor.y + monitor.height + y_offset, fill="lightblue", outline="black", width="5")
            self.canvas.create_text(monitor.x + x_offset + 0.5*monitor.width, monitor.y + y_offset + 0.5*monitor.height, text=monitor.name, font=("Arial", 20))

        self.canvas.scale("all", 0, 0, scale, scale)


