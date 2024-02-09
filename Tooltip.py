"""
@author: supercam19
@github: https://github.com/supercam19
@license: MIT
@description: Mouse hover tooltips that can be attached to widgets
"""

import customtkinter as ctk


class Tooltip:
    # Mouse hover tooltips that can be attached to widgets
    def __init__(self, widget, text):
        self.wait_time = 500  # milliseconds
        self.wrap_length = 180
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.schedule, add="+")
        self.widget.bind("<Leave>", lambda e: self.widget.after(5, self.leave), add="+")
        self.widget.bind("<ButtonPress>", self.leave, add="+")
        self.id = None
        self.tw = None
        self.label = None
        self.over_tooltip = False

    def leave(self, event=None):
        if not self.over_tooltip:
            self.unschedule()
            self.hide_tip()

    def schedule(self, event=None):
        self.id = self.widget.after(self.wait_time, self.show_tip)

    def unschedule(self):
        # Unschedule scheduled popups
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def tt_enter(self, event=None):
        if not self.over_tooltip:
            self.over_tooltip = True

    def tt_leave(self, event=None):
        if self.over_tooltip:
            self.over_tooltip = False
            self.leave()

    def show_tip(self, event=None):
        # Get the position the tooltip needs to appear at
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_pointerx() + 1
        y += self.widget.winfo_pointery() + 1
        self.tw = ctk.CTkToplevel(self.widget)
        self.tw.withdraw()
        self.tw.wm_attributes("-toolwindow", True)
        # Leaves only the label and removes the topbar of the window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry(f'+{x}+{y}')
        """
        The background colour and the foreground colour need to be really similar because the label widget
        has un-removable anti-aliasing that makes the colors blend -> there will be different colour pixels
        on the edge of the label.
        """
        self.tw.wm_attributes('-transparentcolor', '#555555')
        self.tw.configure(bg="#555555")
        self.label = ctk.CTkLabel(self.tw, text=self.text, corner_radius=10, bg_color='#555555', fg_color='#545454', width=1)
        self.label.pack()
        self.label.bind("<Enter>", self.tt_enter, add="+")
        self.label.bind("<Leave>", self.tt_leave, add="+")
        self.tw.geometry = self.label.winfo_width() + 1, self.label.winfo_height() + 1
        self.tw.deiconify()

    def hide_tip(self):
        self.unschedule()
        if self.tw: self.tw.withdraw()