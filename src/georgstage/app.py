"""Georgstage app"""

import logging
import os
import random
import sys
import tkinter as tk
import traceback
from hashlib import sha256
from pathlib import Path
from tkinter import messagebox as mb
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from typing import Any, Optional

from georgstage.export import Exporter
from georgstage.icon_data import ICON_DATA
from georgstage.registry import Registry
from georgstage.tabs.afmønstringer import AfmønstringTab
from georgstage.tabs.statistik import StatistikTab
from georgstage.tabs.vagtliste import VagtListeTab
from georgstage.tabs.vagtperioder import VagtPeriodeTab
from georgstage.util import Style, get_default_font_size, get_project_version, osx_set_process_name

if os.name == 'nt':
    from ctypes import windll  # type: ignore

    windll.shcore.SetProcessDpiAwareness(1)


class App:
    """Georgstage app"""

    def __init__(self) -> None:
        self.setup_logger()

        self.root = tk.Tk()
        self.root.geometry('850x475' if sys.platform == 'darwin' else '850x570')

        self.style = Style(self.root)
        self.style.theme_use('default')
        self.style.configure('Borderless.TNotebook', borderwidth=0, extends='TNotebook')
        self.style.configure(
            'Danger.TButton',
            font=('TkDefaultFont', get_default_font_size(), 'bold'),
            foreground='red',
            extends='TButton',
        )

        try:
            logo = tk.PhotoImage(data=ICON_DATA)
            self.root.iconphoto(True, logo)
        except Exception:
            logging.error('Failed to load icon')
            pass

        self.tab_control = ttk.Notebook(self.root)
        self.registry = Registry()
        self.file_path: Optional[Path] = None
        self.out_of_sync = False
        self.exporter = Exporter(self.registry)

        self.set_window_title()
        if sys.platform == 'darwin':
            osx_set_process_name(b'Georg Stage')

        # Make menu
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        file_menu = tk.Menu(menu)
        menu.add_cascade(label='Filer', menu=file_menu)
        file_menu.add_command(label='Åben vagtplan...', command=self.open_file, accelerator='Ctrl-O')
        file_menu.add_command(label='Gem vagtplan', command=self.save_file, accelerator='Ctrl-S')
        file_menu.add_command(label='Print...', command=self.print_some)
        file_menu.add_command(label='Print alle', command=self.print_all, accelerator='Ctrl-P')
        edit_menu = tk.Menu(menu)
        menu.add_cascade(label='Rediger', menu=edit_menu)
        edit_menu.add_command(label='Fortryd', command=self.undo, accelerator='Ctrl-Z')
        edit_menu.add_command(label='Annuller fortryd', command=self.redo, accelerator='Ctrl-Y')
        self.root.bind('<Control-o>', lambda _: self.open_file())
        self.root.bind('<Control-s>', lambda _: self.save_file())
        self.root.bind('<Control-p>', lambda _: self.print_all())
        self.root.bind('<Control-z>', lambda _: self.undo())
        self.root.bind('<Control-y>', lambda _: self.redo())

        help_menu = tk.Menu(menu)
        menu.add_cascade(label='Hjælp', menu=help_menu)
        help_menu.add_command(
            label='Om Georg Stage vagtplanlægger', command=lambda: mb.showinfo('Om', 'Georg Stage vagtplanlægger')
        )

        self.tabs = {
            'Vagtperioder': VagtPeriodeTab(self.tab_control, self.registry),
            'Vagtliste': VagtListeTab(self.tab_control, self.registry),
            'Afmønstringer': AfmønstringTab(self.tab_control, self.registry),
            'Statistik': StatistikTab(self.tab_control, self.registry),
        }

        for key, value in self.tabs.items():
            self.tab_control.add(value, text=key)

        self.tab_control.pack(padx=0, pady=(0, 0), expand=1, fill='both')
        self.tab_control.bind(
            '<<NotebookTabChanged>>',
            lambda _: list(self.tabs.values())[self.tab_control.index('current')].focus_set(),  # type: ignore
        )

        # 6. bakke REPRESENT
        ttk.Label(
            self.root,
            text=' Made by Mathias Gredal (6. bakke!!!) ',
            font=f'TkDefaultFont {get_default_font_size() - 1} italic',
        ).place(relx=1, y=2.5, anchor='ne')

        # Do a periodic check if we are out of sync
        self.root.after(1000, self.check_sync)

        tk.Tk.report_callback_exception = self.handle_exception

    def run(self) -> None:
        """Run the app"""
        self.root.mainloop()

    def print_all(self) -> None:
        """Print all vagtliste"""
        self.exporter.export_vls(self.registry.vagtlister)

    def print_some(self) -> None:
        """Print some vagtliste"""
        mb.showinfo('Print', 'Ikke implementeret endnu, print alle i stedet')
        self.print_all()

    def open_file(self) -> None:
        """Open a file"""
        try:
            self.file_path = Path(askopenfilename(filetypes=[('Georg Stage Vagtplan', '*.json')]))
            if self.file_path is not None:
                self.registry.load_from_file(self.file_path)
                self.registry.versions.clear()
                self.registry.redo_stack.clear()
                self.set_window_title()
            else:
                mb.showerror('Fejl', 'Filen blev ikke åbnet')
        except FileNotFoundError:
            mb.showerror('Fejl', 'Filen kunne ikke findes')
        except Exception as e:
            self.file_path = None
            logging.exception('An error occurred while opening the file')
            raise e
        finally:
            self.root.focus_force()

    def save_file(self) -> None:
        """Save a file"""
        if self.file_path is not None:
            self.registry.save_to_file(self.file_path)
            return

        result = asksaveasfilename(filetypes=[('Georg Stage Vagtplan', '*.json')])
        if result:
            self.file_path = Path(result)
            if not self.file_path.name.endswith('.json'):
                self.file_path = self.file_path.with_suffix('.json')
            self.registry.save_to_file(self.file_path)
            self.set_window_title()
        else:
            mb.showerror('Fejl', 'Filen blev ikke gemt')

    def undo(self) -> None:
        """Undo the last update"""
        self.registry.undo_last_update()
        self.set_window_title()

    def redo(self) -> None:
        """Redo the last update"""
        self.registry.redo_last_update()
        self.set_window_title()

    def check_sync(self) -> None:
        """Check if the registry is out of sync"""
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
        """Set the window title"""
        version = get_project_version()
        base_title = f'Georg Stage({version}) - Vagtlister'

        if self.out_of_sync:
            base_title = '*' + base_title

        if self.file_path is not None:
            self.root.title(f'{base_title} ({self.file_path.resolve()})')
        else:
            self.root.title(f'{base_title} (ingen fil)')

    def handle_exception(self, *args: Any) -> None:
        """Handle an exception"""
        err = traceback.format_exception(*args)
        logging.error(''.join(err))
        mb.showwarning('Fejl', err[-1])

    def setup_logger(self) -> None:
        """Setup the logger"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
        )


if __name__ == '__main__':
    app = App()
    app.run()
