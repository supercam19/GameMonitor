"""
@author: supercam19
@github: https://github.com/supercam19
@license: MIT
@description: Mouse hover tooltips that can be attached to widgets
"""

import customtkinter as ctk


class Tooltip(ctk.CTkToplevel):
    def __init__(self, widget, text, follow_mouse=True):
        self.widget = widget
        super().__init__(self.widget)
        self.withdraw()
        self.text = text
        self.widget.bind("<Enter>", self.show_tip, add="+")
        self.widget.bind("<Leave>", self.hide_tip, add="+")
        self.widget.bind("<ButtonPress>", self.hide_tip, add="+")

        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_pointerx() + 10
        y += self.widget.winfo_pointery() + 10
        self.wm_attributes("-toolwindow", True)
        # Leaves only the label and removes the topbar of the window
        self.wm_overrideredirect(True)
        self.wm_geometry(f'+{x}+{y}')
        self.wm_attributes("-transparentcolor", "#e3e3e3") if ctk.get_appearance_mode() == "Light" else self.wm_attributes("-transparentcolor", "#555555")
        self.configure(bg=("#bdbdbd", "#555555"))
        self.label = ctk.CTkLabel(self, text=self.text, corner_radius=10, bg_color=("#e3e3e3", '#555555'), fg_color=("#e4e4e4", '#545454'),
                                  width=1)
        self.label.pack()

        if follow_mouse:
            self.widget.bind("<Motion>", self.move_tip, add="+")

    def show_tip(self, event=None):
        self.wm_geometry(f'+{self.widget.winfo_pointerx() + 10}+{self.widget.winfo_pointery() + 10}')
        self.deiconify()

    def hide_tip(self, event=None):
        self.withdraw()

    def move_tip(self, event):
        x, y, cx, cy = self.widget.bbox("insert")
        x = self.widget.winfo_pointerx() + 10
        y = self.widget.winfo_pointery() + 10
        self.wm_geometry(f'+{x}+{y}')

    def set_text(self, text):
        self.text = text
        self.label.config(text=self.text)

