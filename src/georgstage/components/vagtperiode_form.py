from tkinter import ttk
import tkinter as tk


class VagtPeriodeForm(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, padding=(0, 0, 0, 0), *args, **kwargs)

        self.vagtperiode_type = tk.StringVar()
