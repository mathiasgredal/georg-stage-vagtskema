import os
import tkinter as tk
from tkinter import ttk

from georgstage.tabs.export import ExportTab
from georgstage.tabs.statistik import StatistikTab
from georgstage.tabs.vagtliste import VagtListeTab
from georgstage.tabs.vagtperioder import VagtPeriodeTab
from georgstage.registry import Registry

if os.name == 'nt':
    from ctypes import windll  # type: ignore

    windll.shcore.SetProcessDpiAwareness(1)


class App:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.geometry('850x450')
        self.root.title('Georg Stage - Vagtlister')

        self.style = ttk.Style(self.root)
        self.style.theme_use('default')

        tabControl = ttk.Notebook(self.root)
        self.registry = Registry()

        self.tabs = {
            'Vagtperioder': VagtPeriodeTab(tabControl, self.registry),
            'Vagtliste': VagtListeTab(tabControl, self.registry),
            # 'Afmønstringer': StatistikTab(tabControl),
            'Statistik': StatistikTab(tabControl, self.registry),
            'Eksport': ExportTab(tabControl),
        }

        for key, value in self.tabs.items():
            tabControl.add(value, text=key)

        tabControl.pack(padx=0, pady=(0, 0), expand=1, fill='both')
        tabControl.bind(
            '<<NotebookTabChanged>>', lambda event: list(self.tabs.values())[tabControl.index('current')].focus_set()
        )
        ttk.Label(self.root, text=' Made by Mathias Gredal (6. bakke!!!) ', font='TkDefaultFont 12 italic').place(
            relx=1, y=2.5, anchor='ne'
        )

    def run(self) -> None:
        self.root.mainloop()


if __name__ == '__main__':
    app = App()
    app.run()
