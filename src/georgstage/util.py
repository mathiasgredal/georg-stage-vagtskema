"""Util functions"""

import dataclasses
import datetime
import enum
import json
import logging
import sys
import tkinter as tk
import uuid
from pathlib import Path
from tkinter import font, ttk
from typing import Any, Optional, Union

import tomllib


class EnhancedJSONEncoder(json.JSONEncoder):
    """A JSON encoder that supports encoding of dataclasses, datetime objects, UUIDs, and enum members.

    This encoder extends the standard JSONEncoder to handle additional Python data types that are not natively
    serializable by the default encoder. It converts dataclass instances to dictionaries, formats datetime objects
    to ISO 8601 strings, converts UUIDs to their string representation, and encodes enum members by their values.
    """

    def default(self, obj: Any) -> Any:
        """Convert a Python object to a JSON-serializable format.

        This method is called by the JSON encoder when it encounters an object
        that is not natively serializable. It handles dataclass instances,
        datetime objects, UUIDs, and enum members by converting them to
        appropriate JSON-compatible representations.

        Args:
            obj: The object to be encoded.

        Returns:
            The JSON-serializable representation of the object.
        """
        if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
            return dataclasses.asdict(obj)
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, enum.Enum):
            return obj.value
        return super().default(obj)

    def encode(self, obj: Any) -> str:
        """Encode a Python object to a JSON string.

        This method encodes the object using the EnhancedJSONEncoder and
        ensures that all dataclass instances, datetime objects, UUIDs,
        and enum members are properly converted to their JSON-compatible
        representations.
        """
        return super().encode(self.valuify_dict(obj))

    def valuify_dict(self, obj: Any) -> Any:
        """Convert a Python object to a dictionary of values.

        This method recursively converts dataclass instances, lists,
        dictionaries, and enum members to their JSON-compatible
        representations.
        """
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
    """A JSON decoder that supports decoding of JSON strings into Python objects.

    This decoder extends the standard JSONDecoder to handle additional JSON-compatible
    representations of Python data types. It converts ISO 8601 strings to datetime objects,
    and UUID strings to their UUID representation.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)  # noqa: B026

    def object_hook(self, obj: Any) -> Any:
        """Convert a JSON object to a Python object.

        This method is called by the JSON decoder when it encounters a JSON object.
        It converts ISO 8601 strings to datetime objects, and UUID strings to their UUID representation.
        """
        ret: dict[str, Any] = {}
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
    """A style manager for ttk widgets.

    This class extends the ttk.Style class to provide a more flexible and
    user-friendly way to customize the appearance and behavior of ttk widgets.
    It allows for easy configuration of widget styles, including the ability to
    extend existing styles and apply customizations.
    """

    EXTENDS = 'extends'

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent)
        self._style: dict[Any, Any] = {}

    def configure(self, style: Any, query_opt: Any | None = ..., **kwargs: Any) -> Any:
        """Configure a widget style.

        This method allows for the configuration of widget styles by setting
        specific properties and values. It extends the ttk.Style class to
        provide a more flexible and user-friendly way to customize the appearance
        and behavior of ttk widgets.
        """
        self._style.setdefault(style, {}).update(kwargs)

        extends = self._style.get(kwargs.get(Style.EXTENDS), {})
        super().configure(style, **extends)

        super().configure(style, **kwargs)


def make_cell(
    parent: tk.Misc,
    row: int,
    col: int,
    text: str,
    width: int,
    readonly: bool,
    sv: Optional[Union[tk.StringVar, tk.IntVar]] = None,
    bg_color: str = 'white',
    fg_color: str = 'black',
    bold: bool = False,
    **kw: Any,
) -> None:
    """Create a standard cell for a table."""
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


def osx_set_process_name(app_title: bytes) -> bool:
    """Change OSX application title"""
    from ctypes import Structure, c_int, cdll, pointer
    from ctypes.util import find_library

    lib_name = find_library('ApplicationServices')

    if lib_name is None:
        logging.error('cannot run without OS X window manager')
        return False

    app_services = cdll.LoadLibrary(lib_name)

    if app_services.CGMainDisplayID() == 0:
        logging.error('cannot run without OS X window manager')
    else:

        class ProcessSerialNumber(Structure):
            _fields_ = [('highLongOfPSN', c_int), ('lowLongOfPSN', c_int)]

        psn = ProcessSerialNumber()
        psn_p = pointer(psn)
        if (app_services.GetCurrentProcess(psn_p) < 0) or (app_services.SetFrontProcess(psn_p) < 0):
            logging.error('cannot run without OS X gui process')

        app_services.CPSSetProcessName(psn_p, app_title)

    return False


def get_default_font_size() -> int:
    """Get the default font size for the current platform"""
    return font.nametofont('TkDefaultFont').actual()['size']


def get_project_version():
    """Get version of project based on pyproject.toml"""
    pyproject_toml_file = Path(__file__).parent.parent.parent / 'pyproject.toml'
    if pyproject_toml_file.exists() and pyproject_toml_file.is_file():
        return f'v{tomllib.loads(pyproject_toml_file.read_text())["project"]["version"]}'
    return 'unknown'
