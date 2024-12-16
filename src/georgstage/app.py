import os
import tkinter as tk
from tkinter import ttk

from georgstage.export import Exporter
from georgstage.tabs.statistik import StatistikTab
from georgstage.tabs.vagtliste import VagtListeTab
from georgstage.tabs.vagtperioder import VagtPeriodeTab
from georgstage.tabs.afmønstringer import AfmønstringTab
from georgstage.registry import Registry
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import messagebox as mb
from pathlib import Path
from hashlib import sha256

if os.name == 'nt':
    from ctypes import windll  # type: ignore

    windll.shcore.SetProcessDpiAwareness(1)


class App:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.geometry('850x450')

        self.style = ttk.Style(self.root)
        self.style.theme_use('default')

        tabControl = ttk.Notebook(self.root)
        self.registry = Registry()
        self.file_path: Path | None = None
        self.out_of_sync = False
        self.exporter = Exporter()

        self.set_window_title()

        # Make menu
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        file_menu = tk.Menu(menu)
        menu.add_cascade(label='Filer', menu=file_menu)
        file_menu.add_command(label='Åben vagtplan...', command=self.open_file, accelerator='Ctrl-O')
        file_menu.add_command(label='Gem vagtplan', command=self.save_file, accelerator='Ctrl-S')
        file_menu.add_command(label='Print...', command=self.print_some)
        file_menu.add_command(label='Print alle', command=self.print_all, accelerator='Ctrl-P')
        self.root.bind('<Control-o>', lambda _: self.open_file())
        self.root.bind('<Control-s>', lambda _: self.save_file())
        self.root.bind('<Control-p>', lambda _: self.print_all())

        help_menu = tk.Menu(menu)
        menu.add_cascade(label='Hjælp', menu=help_menu)
        help_menu.add_command(
            label='Om Georg Stage vagtplanlægger', command=lambda: mb.showinfo('Om', 'Georg Stage vagtplanlægger')
        )

        self.tabs = {
            'Vagtperioder': VagtPeriodeTab(tabControl, self.registry),
            'Vagtliste': VagtListeTab(tabControl, self.registry),
            'Afmønstringer': AfmønstringTab(tabControl, self.registry),
            'Statistik': StatistikTab(tabControl, self.registry),
        }

        for key, value in self.tabs.items():
            tabControl.add(value, text=key)

        tabControl.pack(padx=0, pady=(0, 0), expand=1, fill='both')
        tabControl.bind(
            '<<NotebookTabChanged>>', lambda _: list(self.tabs.values())[tabControl.index('current')].focus_set()
        )

        # 6. bakke REPRESENT
        ttk.Label(self.root, text=' Made by Mathias Gredal (6. bakke!!!) ', font='TkDefaultFont 12 italic').place(
            relx=1, y=2.5, anchor='ne'
        )

        # Do a periodic check if we are out of sync
        self.root.after(1000, self.check_sync)

    def run(self) -> None:
        self.root.mainloop()

    def print_all(self) -> None:
        self.exporter.export_vls(self.registry.vagtlister)
    
    def print_some(self) -> None:
        mb.showinfo('Print', 'Ikke implementeret endnu, print alle i stedet')
        self.print_all()

    def open_file(self) -> None:
        try:
            self.file_path = Path(askopenfilename(filetypes=[('Georg Stage Vagtplan', '*.json')]))
            if self.file_path is not None:
                self.registry.load_from_file(self.file_path)
                self.set_window_title()
                self.root.focus_force()
            else:
                mb.showerror('Fejl', 'Filen blev ikke åbnet')
        except FileNotFoundError:
            mb.showerror('Fejl', 'Filen kunne ikke findes')

    def save_file(self) -> None:
        if self.file_path is not None:
            self.registry.save_to_file(self.file_path)
            return

        self.file_path = Path(asksaveasfilename(filetypes=[('Georg Stage Vagtplan', '*.json')]))
        if self.file_path is not None:
            self.registry.save_to_file(self.file_path)
            self.set_window_title()
        else:
            mb.showerror('Fejl', 'Filen blev ikke gemt')

    def check_sync(self) -> None:
        if self.file_path is not None:
            on_disk_registry = self.file_path.read_text()
            in_memory_registry = self.registry.save_to_string()
            if sha256(on_disk_registry.encode()).hexdigest() == sha256(in_memory_registry.encode()).hexdigest():
                self.out_of_sync = False
            else:
                self.out_of_sync = True
            self.set_window_title()
        self.root.after(1000, self.check_sync)

    def set_window_title(self) -> None:
        base_title = 'Georg Stage - Vagtlister'

        if self.out_of_sync:
            base_title = '*' + base_title

        if self.file_path is not None:
            self.root.title(f'{base_title} ({self.file_path.resolve()})')
        else:
            self.root.title(f'{base_title} (ingen fil)')


if __name__ == '__main__':
    app = App()
    app.run()
