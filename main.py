import sys
import time

import comtypes

import customtkinter as ctk
import psutil
import win32com.client
import wmi
import screeninfo
from gmutils import *
import threading
import infi.systray
from tkinter import filedialog, PhotoImage
from Tooltip import Tooltip
import winreg as reg
import webbrowser


class Window(ctk.CTk):
    def __init__(self):

        self.flag_data_refresh = False

        super().__init__()
        self.games_list_len = 0
        self.title("GameMonitor")
        # self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        if os.path.isfile("icon.ico"): self.iconbitmap("icon.ico")
        self.visible = True
        self.toplevels = []

        # Place window in the middle of the screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        x = (screen_width / 2) - (window_width / 2)
        y = (screen_height / 2) - (window_height / 2)
        self.geometry('500x400+%d+%d' % (x, y + 30))
        self.minsize(450, 360)

        self.title_frame = ctk.CTkFrame(self, fg_color=("#ffffff", "#272727"), bg_color=("#ffffff", "#272727"))
        self.title_frame.pack(side='top', fill='x')

        self.reveal_monitors = ctk.CTkButton(self.title_frame, text="?", command=self.reveal_monitors,
                                             fg_color=("#ffffff", "#272727"), text_color=("black", "white"),
                                             hover_color=("#f6f6f6", "#2b2b2b"), width=20, font=("Arial", 20), corner_radius=8)
        self.reveal_monitors.pack(padx=10, pady=5, side='left')
        self.reveal_monitors_tt = Tooltip(self.reveal_monitors, "Show monitor names")

        self.add_game = ctk.CTkButton(self.title_frame, text="+", command=lambda: add_game(self), hover_color=("#f6f6f6", "#2b2b2b"),
                                      fg_color=("#ffffff", "#272727"), width=20, font=("Arial", 20), corner_radius=8, text_color=("black", "white"))
        self.add_game.pack(padx=10, pady=5, side='right')
        self.add_game_tt = Tooltip(self.add_game, "Add game")

        self.title_button = ctk.CTkButton(self.title_frame, text="GameMonitor", font=("Arial", 20, "bold"), command=lambda: webbrowser.open("https://github.com/supercam19/GameMonitor"),
                                          fg_color=("#ffffff", "#272727"), bg_color=("#ffffff", "#272727"), hover=False, width=0, text_color=("black", "white"))
        self.title_button.pack(pady=10)
        self.title_button.bind("<Enter>", self.title_hovered)
        self.title_button.bind("<Leave>", self.title_leave)

        self.games_list_frame = ctk.CTkScrollableFrame(self, width=500, fg_color=("#ffffff", "#272727"), bg_color=("#ffffff", "#272727"))
        self.games_list_frame.pack(side="top", fill="both", expand=True)

        self.options_frame = ctk.CTkFrame(self, fg_color=("#ffffff", "#272727"), bg_color=("#ffffff", "#272727"))
        self.options_frame.pack(side='top', fill='x')

        self.enable_startup_fr = ctk.CTkFrame(self.options_frame, fg_color=("#ffffff", "#272727"), bg_color=("#ffffff", "#272727"))
        self.enable_startup_fr.pack(fill='x')
        self.enable_startup_lbl = ctk.CTkLabel(self.enable_startup_fr, text="Enable on startup", font=("Arial", 14))
        self.enable_startup_lbl.pack(side='left', padx=10)
        self.enable_startup_sw = ctk.CTkSwitch(self.enable_startup_fr, command=self.toggle_startup, text="", width=0)
        self.enable_startup_sw.pack(side='right', padx=10)
        self.enable_startup_sw.select() if json_read_safe_default("settings.json", "startup", 0) else self.enable_startup_sw.deselect()

        self.default_monitor_fr = ctk.CTkFrame(self.options_frame, fg_color=("#ffffff", "#272727"), bg_color=("#ffffff", "#272727"))
        self.default_monitor_fr.pack(fill='x')
        self.default_monitor_lbl = ctk.CTkLabel(self.default_monitor_fr, text="Default Monitor", font=("Arial", 14))
        self.default_monitor_lbl.pack(side='left', padx=10)
        self.default_monitor_select = ctk.CTkOptionMenu(self.default_monitor_fr, values=get_monitors(True), command=self.update_default_monitor)
        self.default_monitor_select.pack(side='right', padx=10, pady=5)

    def toggle_startup(self):
        settings = load_settings()
        settings["startup"] = self.enable_startup_sw.get()
        save_settings(settings)

        # Create a .bat file in the startup folder
        if self.enable_startup_sw.get():
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, "Software\Microsoft\Windows\CurrentVersion\Run", 0, reg.KEY_ALL_ACCESS)
            reg.SetValueEx(key, "GameMonitor", 0, reg.REG_SZ, sys.argv[0] + " --startup")
        else:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, "Software\Microsoft\Windows\CurrentVersion\Run", 0, reg.KEY_ALL_ACCESS)
            reg.DeleteValue(key, "GameMonitor")

    def update_default_monitor(self, choice):
        global default_monitor
        settings = load_settings()
        default_monitor = get_monitor_id_from_name(choice)
        settings["default_monitor"] = default_monitor
        save_settings(settings)

    def reveal_monitors(self):
        MonitorPreview(self)

    def title_hovered(self, e):
        self.title_button.configure(font=("Arial", 20, "bold", "underline"))

    def title_leave(self, e):
        self.title_button.configure(font=("Arial", 20, "bold"))


class Game:
    def __init__(self, name, process_name, path, monitor, window):
        self.name = name
        self.process_name = process_name
        self.path = path
        self.game_fr = None
        self.game_nm = None
        self.game_monitor_select = None
        self.monitor = monitor
        self.window = window

    def update_monitor(self, monitor):
        self.monitor = self.game_monitor_select.get()
        settings = load_settings()
        for game in settings["games"]:
            if game["path"] == self.path:
                game["monitor"] = get_monitor_id_from_name(self.monitor)
                save_settings(settings)
                break
        self.window.flag_data_refresh = True

    def add_to_window(self, window):
        colour = ("#ececec", "#333333") if window.games_list_len % 2 == 0 else ("#f6f6f6", "#2b2b2b")
        window.games_list_len += 1
        self.game_fr = ctk.CTkFrame(window.games_list_frame, bg_color=colour, fg_color=colour)
        self.game_fr.pack(fill="x")
        self.game_nm = ctk.CTkLabel(self.game_fr, text="  " + self.name, font=("Arial", 16), image=icon_from_exe(self.path), compound="left")
        self.game_nm.pack(side="left", padx=10)
        self.game_monitor_select = ctk.CTkOptionMenu(self.game_fr, values=get_monitors(True), command=self.update_monitor)
        self.game_monitor_select.pack(side="right", padx=10, pady=5)
        self.game_monitor_select.set(get_monitors(True)[self.monitor])


class ProcessListener(threading.Thread):
    def __init__(self, games, window):
        super().__init__()
        self.games = games
        self.sleepy_time = False
        self.c = None
        self.process_watcher = None
        self.window = window
        self.last_monitor_switch_time = 0

    def run(self):
        comtypes.CoInitialize()
        process_names = [game.process_name for game in self.games]
        self.c = wmi.WMI()
        self.process_watcher = self.c.Win32_Process.watch_for("creation")
        while not self.sleepy_time:
            try:
                new_process = self.process_watcher(timeout_ms=1000)
                if new_process.Name in process_names:
                    for game in self.games:
                        if game.process_name == new_process.Name:
                            if self.window:
                                pid = get_pid_from_name(game.process_name)
                                if pid:
                                    p = psutil.Process(pid)
                                    p.suspend()
                                    self.window.after(2500, p.resume)
                            if self.last_monitor_switch_time + 2 < time.time():
                                result = set_monitor(game.monitor)
                                if result:
                                    self.last_monitor_switch_time = time.time()
                                    self._wait_for_process_end(game)
            except wmi.x_wmi_timed_out:
                if self.window.flag_data_refresh:
                    self.games = load_games(self.window)
                    process_names = [game.process_name for game in self.games]
                    self.window.flag_data_refresh = False

    def _wait_for_process_end(self, game):
        if not self.c: raise Exception("WMI not initialized")
        self.process_monitor = self.c.Win32_Process.watch_for("deletion")
        while not self.sleepy_time:
            try:
                deleted_process = self.process_monitor(timeout_ms=1000)
                if deleted_process.Name == game.process_name:
                    set_monitor(default_monitor)
                    return
            except wmi.x_wmi_timed_out:
                continue

    def stop(self):
        self.sleepy_time = True


def get_monitors(name_only=False):
    monitors = screeninfo.get_monitors()
    names = []
    if not name_only:
        for i in range(len(monitors)):
            names.append((monitors[i].name, None, lambda e, i=i: set_monitor(i)))
    else:
        for monitor in monitors:
            names.append(monitor.name)
    return names


def set_monitor(monitor):
    monitors = screeninfo.get_monitors()
    if monitors[monitor].is_primary == False:
        os.chdir(".")
        try:
            os.system(f"displayz.exe set-primary --id {monitor}")
            # subprocess.call([f"displayz.exe set-primary --id {monitor}"])
            return True
        except:
            return False
    return False


def spawn_window(window):
    window.deiconify()
    window.visible = True


def add_game(window):
    path = filedialog.askopenfilename(title="Select a game's executable file", filetypes=(("Game executable", "*.exe"),))
    settings = load_settings()
    for game in settings["games"]:
        if game["path"] == path:
            popup("Game already added", "This game has already been added to the list.")
            return
    name = getFileProperties(path)
    filename = os.path.basename(path)
    game = Game(name, filename, path, 0, window)
    game.add_to_window(window)

    settings["games"].append({"name": name, "process_name": filename, "path": path, "monitor": 0})
    save_settings(settings)
    window.flag_data_refresh = True


def launch_game(game_name):
    games = load_settings()["games"]
    if os.path.exists(game_name):
        exe = os.path.basename(game_name)
        for game in games:
            if game.get('process_name') == exe:
                set_monitor(game.get('monitor'))
                time.sleep(2)
        os.system(game_name)
        set_monitor(default_monitor)
        sys.exit(0)
    else:
        for game in games:
            if game.get("name") == game_name:
                set_monitor(game.get("monitor"))
                time.sleep(2)
                os.chdir(os.path.dirname(game.get('path')))
                os.system(f"\"{game.get('process_name')}\"")
                set_monitor(default_monitor)
                sys.exit(0)


def load_games(window):
    games_data = load_settings().get("games")
    games = []
    for i, game in enumerate(games_data):
        if os.path.exists(game.get("path")):
            games.append(Game(game.get("name"), game.get("process_name"), game.get("path"), game.get("monitor"), window))
        else:
            del games_data[i]
    save_settings({"games": games_data})
    return games


def main(open_window):
    ctk.set_appearance_mode("system")

    window = Window()
    games = load_games(window)
    listener = ProcessListener(games, window)
    listener.start()

    for game in games:
        game.add_to_window(window)

    if not open_window:
        window.withdraw()
        window.visible = False

    names = get_monitors()
    menu_options = (("Settings", None, lambda e: spawn_window(window)), ("Set Primary", None, names))
    systray = infi.systray.SysTrayIcon("icon.ico", "GameMonitor", menu_options, on_quit=lambda e: window.quit())
    systray.start()

    window.mainloop()
    # stop the other threads
    listener.stop()
    listener.join()


if __name__ == "__main__":
    try:
        os.chdir(os.path.realpath(os.path.dirname(sys.argv[0])))
        check_files()

        default_monitor = 0
        show_on_startup = False if "--startup" in sys.argv else True

        for i, arg in enumerate(sys.argv):
            show_on_startup = False if arg == '--startup' else True
            if arg == '--launch-game' and len(sys.argv) > i + 1:
                launch_game(sys.argv[i + 1])

        main(show_on_startup)
    except Exception as e:
        popup("Error", f"An error occurred. If you believe this to be a bug, please submit an issue at github.com/supercam19/GameMonitor/issues with the error message:\n\n{e.with_traceback(None)}")

