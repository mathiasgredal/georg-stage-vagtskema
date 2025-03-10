"""Responsive notebook component"""

from tkinter import ttk
from typing import Any


class ResponsiveNotebook(ttk.Frame):
    """A tkinter Notebook, which actually displays the tab content, when the tab is selected."""

    def __init__(self, parent: ttk.Frame, *args: Any, **kw: Any) -> None:
        ttk.Frame.__init__(self, parent, *args, **kw)

        self.tabs: dict[str, ttk.Frame] = {}

        # GUI Elements
        self.tab_control = ttk.Notebook(self, style='Borderless.TNotebook')
        self.tab_stack = ttk.Frame(self)

        # Layout
        self.tab_control.grid(row=0, column=0, sticky='new')
        self.tab_stack.grid(row=1, column=0, sticky='nsew')

        self.tab_stack.grid_columnconfigure(0, weight=1)
        self.tab_stack.grid_rowconfigure(0, weight=1)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Bindings
        self.tab_control.bind(
            '<<NotebookTabChanged>>',
            lambda _: list(self.tabs.values())[self.tab_control.index('current')].tkraise(),  # type: ignore
        )

    def add(self, tab_name: str, tab_frame: ttk.Frame) -> None:
        """Add a tab to the notebook."""
        self.tabs[tab_name] = tab_frame
        self.tab_control.add(ttk.Frame(self), text=tab_name)
        tab_frame.grid(row=0, column=0, sticky='nsew')
