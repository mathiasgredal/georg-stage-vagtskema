import dataclasses
import json
import datetime
import tkinter as tk
import pathlib
import enum
import uuid
from georgstage.model import VagtPeriode, VagtListe

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
        json.JSONDecoder.__init__(
            self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        ret = {}
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

def make_cell(
    parent: tk.Misc, row: int, col: int, text: str, width: int, readonly: bool, sv: tk.StringVar | None = None, **kw
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
    entry1.grid(row=row, column=col + 2, **kw)


if __name__ == "__main__":
    target = pathlib.Path("/Users/mathiasgredal/Desktop/vagtplan.json").read_text()
    data = json.loads(target, cls=EnhancedJSONDecoder)
    vl = VagtListe(**data["vagtlister"][0])
    print(vl)
    # print(json.dumps(vl, cls=EnhancedJSONEncoder, indent=4))
