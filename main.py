import sys

import comtypes

import customtkinter as ctk
import wmi
import screeninfo
from gmutils import *
import threading
import infi.systray
from tkinter import filedialog, PhotoImage
from Tooltip import Tooltip


class Window(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.games_list_len = 0
        self.title("GameMonitor")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        self.iconbitmap("icon.ico")
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

        self.title_frame = ctk.CTkFrame(self)
        self.title_frame.pack(side='top', fill='x')

        #self.reveal_monitors = ctk.CTkButton(self.title_frame, text="\U0001F5B5", command=self.reveal_monitors,
        #                                     fg_color="#2b2b2b",
        #                                     hover_color="#333333", width=20, font=("Arial", 20), corner_radius=8)
        #self.reveal_monitors.pack(padx=10, pady=5, side='left')
        #self.reveal_monitors_tt = Tooltip(self.reveal_monitors, "Reveal monitors IDs")

        self.title_label = ctk.CTkLabel(self.title_frame, text="GameMonitor", font=("Arial", 20, "bold"))
        self.title_label.pack(pady=10, side='left', padx=(200, 0))

        self.add_game = ctk.CTkButton(self.title_frame, text="+", command=lambda: add_game(self), fg_color="#2b2b2b",
                                      hover_color="#333333", width=20, font=("Arial", 20), corner_radius=8)
        self.add_game.pack(padx=10, pady=5, side='right')
        self.add_game_tt = Tooltip(self.add_game, "Add game")

        self.games_list_frame = ctk.CTkScrollableFrame(self, width=500, height=340, fg_color="#2e2e2e", bg_color="#2e2e2e")
        self.games_list_frame.pack(side="top", fill="both", expand=True)

    def reveal_monitors(self):
        self.toplevels = reveal_monitor_ids(self)
        # gotta store in obj memory so they can kill themselves


class Game:
    def __init__(self, name, process_name, path, monitor):
        self.name = name
        self.process_name = process_name
        self.path = path
        self.game_fr = None
        self.game_nm = None
        self.game_monitor_select = None
        self.monitor = monitor

    def update_monitor(self, monitor):
        self.monitor = self.game_monitor_select.get()
        settings = load_settings()
        for game in settings["games"]:
            if game["path"] == self.path:
                game["monitor"] = int(self.monitor[-1])
                save_settings(settings)
                break

    def add_to_window(self, window):
        colour = "#333333" if window.games_list_len % 2 == 0 else "#2b2b2b"
        window.games_list_len += 1
        self.game_fr = ctk.CTkFrame(window.games_list_frame, bg_color=colour, fg_color=colour)
        self.game_fr.pack(fill="x")
        self.game_nm = ctk.CTkLabel(self.game_fr, text=self.name, font=("Arial", 16))
        self.game_nm.pack(side="left", padx=10)
        self.game_monitor_select = ctk.CTkOptionMenu(self.game_fr, values=["Monitor 0", "Monitor 1"], command=self.update_monitor)
        self.game_monitor_select.pack(side="right", padx=10, pady=5)
        self.game_monitor_select.set("Monitor " + str(self.monitor))


class ProcessListener(threading.Thread):
    def __init__(self, games):
        super().__init__()
        self.games = games
        self.sleepy_time = False
        self.c = None
        self.process_watcher = None

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
                            result = set_monitor(game.monitor)
                            if result:
                                self._wait_for_process_end(game)
            except wmi.x_wmi_timed_out:
                continue

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
    game = Game(name, filename, path, 0)
    game.add_to_window(window)

    settings["games"].append({"name": name, "process_name": filename, "path": path, "monitor": 0})
    save_settings(settings)


def main(open_window):
    check_files()
    ctk.set_appearance_mode("system")
    ctk.deactivate_automatic_dpi_awareness() # DPI awareness breaks the scrolling frame
    games_data = load_settings().get("games")
    games = []
    for game in games_data:
        games.append(Game(game.get("name"), game.get("process_name"), game.get("path"), game.get("monitor")))
    listener = ProcessListener(games)
    listener.start()
    window = Window()

    for game in games:
        game.add_to_window(window)

    if not open_window:
        window.withdraw()
        window.visible = False

    menu_options = (("Settings", None, lambda e: spawn_window(window)),)
    systray = infi.systray.SysTrayIcon("icon.ico", "GameMonitor", menu_options, on_quit=lambda e: window.quit())
    systray.start()

    window.mainloop()
    # stop the other threads
    listener.stop()
    listener.join()


if __name__ == "__main__":
    default_monitor = 0
    show_on_startup = False if "--startup" in sys.argv else True
    main(show_on_startup)
