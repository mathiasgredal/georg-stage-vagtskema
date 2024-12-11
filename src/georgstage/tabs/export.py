from tkinter import ttk


class ExportTab(ttk.Frame):
    def __init__(self, parent, *args, **kwargs) -> None:
        ttk.Frame.__init__(self, parent, padding=(5, 5, 12, 0), *args, **kwargs)
        ttk.Label(self, text='Export').pack()
