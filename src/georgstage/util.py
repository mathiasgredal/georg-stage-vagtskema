import dataclasses
import json
from datetime import datetime
import tkinter as tk


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return super().default(obj)


def make_cell(
    parent: tk.Misc, row: int, col: int, text: str, width: int, readonly: bool, sv: tk.StringVar | None = None
) -> None:
    entry1 = tk.Entry(
        parent,
        textvariable=sv if sv is not None else tk.StringVar(parent, value=text),
        width=width,
        highlightthickness=0,
        borderwidth=1,
        relief='ridge',
    )
    if readonly:
        entry1.configure(takefocus=False)
        entry1.configure(state='disabled')
        entry1.configure(disabledbackground='white', disabledforeground='black')
    entry1.grid(row=row, column=col + 2)
