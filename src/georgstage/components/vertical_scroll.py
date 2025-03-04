"""Vertical scroll component"""

import functools
import tkinter as tk
from sys import platform
from tkinter import ttk
from typing import Any

fp = functools.partial


class VerticalScrolledFrame(ttk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    """

    def __init__(self, parent: tk.Misc, *args: Any, **kw: Any) -> None:
        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event: tk.Event) -> None:  # type: ignore
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion=(0, 0, *size))
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())

        def _configure_canvas(event: tk.Event) -> None:  # type: ignore
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())

        if platform == 'linux' or platform == 'linux2':

            def _on_mousewheel(event: tk.Event, scroll: int) -> None:  # type: ignore
                canvas.yview_scroll(int(scroll), 'units')

            def _bind_to_mousewheel(event: tk.Event) -> None:  # type: ignore
                canvas.bind_all('<Button-4>', fp(_on_mousewheel, scroll=-1))
                canvas.bind_all('<Button-5>', fp(_on_mousewheel, scroll=1))

            def _unbind_from_mousewheel(event: tk.Event) -> None:  # type: ignore
                canvas.unbind_all('<Button-4>')
                canvas.unbind_all('<Button-5>')
        elif platform == 'darwin':

            def _on_mousewheel(event: tk.Event) -> object:  # type: ignore
                canvas.yview_scroll(int(-1 * event.delta), 'units')

            def _bind_to_mousewheel(event: tk.Event) -> None:  # type: ignore
                canvas.bind_all('<MouseWheel>', _on_mousewheel)  # type: ignore

            def _unbind_from_mousewheel(event: tk.Event) -> None:  # type: ignore
                canvas.unbind_all('<MouseWheel>')
        elif platform == 'win32':

            def _on_mousewheel(event: tk.Event) -> None:  # type: ignore
                canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

            def _bind_to_mousewheel(event: tk.Event) -> None:  # type: ignore
                canvas.bind_all('<MouseWheel>', _on_mousewheel)  # type: ignore

            def _unbind_from_mousewheel(event: tk.Event) -> None:  # type: ignore
                canvas.unbind_all('<MouseWheel>')

        ttk.Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        self.canvas = canvas = tk.Canvas(self, bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = ttk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior, anchor=tk.NW)

        interior.bind('<Configure>', _configure_interior)
        canvas.bind('<Configure>', _configure_canvas)
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)
