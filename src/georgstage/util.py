import dataclasses
import json
import datetime
import sys
import tkinter as tk
from tkinter import ttk, font
import enum
from typing import Optional
import uuid


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, enum.Enum):
            return obj.value
        return super().default(obj)

    def encode(self, obj):
        return super().encode(self.valuify_dict(obj))

    def valuify_dict(self, obj):
        if dataclasses.is_dataclass(obj):
            new_obj = {}
            for field in dataclasses.fields(obj):
                new_obj[field.name] = self.valuify_dict(obj.__dict__[field.name])
            return new_obj

        if isinstance(obj, list):
            return [self.valuify_dict(item) for item in obj]

        if isinstance(obj, dict):
            new_obj = {}
            for key, value in obj.items():
                if isinstance(key, enum.Enum):
                    new_obj[key.value] = self.valuify_dict(value)
                else:
                    new_obj[key] = self.valuify_dict(value)
            return new_obj

        return obj


class EnhancedJSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        ret = {}
        # TODO: Move this into the post_init method of each dataclass
        for key, value in obj.items():
            if key in {'start', 'end'}:
                ret[key] = datetime.datetime.fromisoformat(value)
            elif key in {'start_date', 'end_date'}:
                ret[key] = datetime.date.fromisoformat(value)
            elif key in {'id', 'vagtperiode_id'}:
                ret[key] = uuid.UUID(value)
            else:
                ret[key] = value
        return ret


class Style(ttk.Style):
    EXTENDS = 'extends'

    def __init__(self, parent):
        super().__init__(parent)
        self._style = {}

    def configure(self, cls, **kwargs):
        self._style.setdefault(cls, {}).update(kwargs)

        extends = self._style.get(kwargs.get(Style.EXTENDS), {})
        super().configure(cls, **extends)

        super().configure(cls, **kwargs)


def make_cell(
    parent: tk.Misc,
    row: int,
    col: int,
    text: str,
    width: int,
    readonly: bool,
    sv: Optional[tk.StringVar] = None,
    bg_color='white',
    fg_color='black',
    bold=False,
    **kw,
) -> None:
    entry1 = tk.Entry(
        parent,
        textvariable=sv if sv is not None else tk.StringVar(parent, value=text),
        width=int(width if sys.platform == 'darwin' else width * 1.2),
        highlightthickness=0,
        borderwidth=1,
        relief='ridge',
        background=bg_color,
        foreground=fg_color,
        font=('TkDefaultFont', get_default_font_size(), 'bold' if bold else 'normal'),
    )
    if readonly:
        entry1.configure(takefocus=False)
        entry1.configure(state='disabled')
        entry1.configure(disabledbackground=bg_color, disabledforeground=fg_color)
    entry1.grid(row=row, column=col + 2, **kw)


def osx_set_process_name(app_title) -> bool:
    """Change OSX application title"""

    from ctypes import cdll, c_int, pointer, Structure
    from ctypes.util import find_library

    app_services = cdll.LoadLibrary(find_library('ApplicationServices'))

    if app_services.CGMainDisplayID() == 0:
        print('cannot run without OS X window manager')
    else:

        class ProcessSerialNumber(Structure):
            _fields_ = [('highLongOfPSN', c_int), ('lowLongOfPSN', c_int)]

        psn = ProcessSerialNumber()
        psn_p = pointer(psn)
        if (app_services.GetCurrentProcess(psn_p) < 0) or (app_services.SetFrontProcess(psn_p) < 0):
            print('cannot run without OS X gui process')

        app_services.CPSSetProcessName(psn_p, app_title)

    return False


def get_default_font_size() -> int:
    """Get the default font size for the current platform"""
    return font.nametofont('TkDefaultFont').actual()['size']
