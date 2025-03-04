"""Fancy table component"""

import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk
from typing import Any

from georgstage.components.vertical_scroll import VerticalScrolledFrame
from georgstage.model import kabys_elev_nrs
from georgstage.util import make_cell

HEADER_COLOR = '#5a80b8'
TINT_COLOR = '#dee5f0'


@dataclass
class HeaderLabel:
    """A label for the header of the table."""

    name: str
    width: int


class FancyTable(ttk.Frame):
    """A fancy table that can be used to display data in a grid."""

    def __init__(
        self,
        parent: ttk.Frame,
        labels: list[HeaderLabel],
        data: dict[tuple[str, int], tk.StringVar],
        col_0_width: int = 3,
        col_0_ipadx: int = 2,
        *args: Any,
        **kw: Any,
    ):
        ttk.Frame.__init__(self, parent, *args, **kw)
        self.col_0_width = col_0_width
        self.col_0_ipadx = col_0_ipadx

        # GUI Elements
        self.header = ttk.Frame(self)
        self.scrollable = VerticalScrolledFrame(self)

        self._make_header(self.header, labels)
        self._make_header(self.scrollable.interior, labels)

        tinted = False
        for row in range(1, 64):
            if row in kabys_elev_nrs:
                continue

            tinted = not tinted
            bg_color = 'white' if tinted == 0 else TINT_COLOR

            make_cell(
                self.scrollable.interior,
                row + 1,
                0,
                str(row),
                self.col_0_width,
                True,
                None,
                bg_color,
                ipadx=self.col_0_ipadx,
            )
            for col, label in enumerate(labels):
                data[(label.name, row)] = tk.StringVar(self, value='0')
                make_cell(
                    self.scrollable.interior, row + 1, col + 1, '', label.width, True, data[(label.name, row)], bg_color
                )

        # Layout
        self.header.place(x=0, y=0, anchor='nw')
        self.scrollable.grid(column=0, row=0, sticky='nsew')
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.header.lift()

    def _make_header(self, parent: ttk.Frame, labels: list[HeaderLabel]) -> None:
        for col, label in enumerate(labels):
            make_cell(parent, 0, col + 1, label.name, label.width, True, None, HEADER_COLOR, 'white', True)

        make_cell(parent, 0, 0, '#', self.col_0_width, True, None, HEADER_COLOR, 'white', True, ipadx=self.col_0_ipadx)
