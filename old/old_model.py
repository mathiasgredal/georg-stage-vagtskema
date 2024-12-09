from dataclasses import dataclass
from enum import Enum

from datetime import date
from dateutil.parser import parse
import pandas as pd


class Opgave(Enum):
    VAGTHAVENDE_ELEV = 0
    ORDONNANS = 1
    UDKIG = 2
    BJAERGEMAERS = 3
    RORGAENGER = 4
    UDSAETNINGSGAST_A = 5
    UDSAETNINGSGAST_B = 6
    UDSAETNINGSGAST_C = 7
    UDSAETNINGSGAST_D = 8
    UDSAETNINGSGAST_E = 9
    PEJLEGAST_A = 10
    PEJLEGAST_B = 11
    DAEKSELEV_I_KABYS = 12
    HU = 13
    UDE = 14


def get_skifte_for_gast(gast):
    if 0 < gast <= 20:
        return 1
    elif 20 < gast <= 40:
        return 2
    else:
        return 3


@dataclass
class Vagt:
    dato: date
    vagt_tid: int
    gast: int
    opgave: Opgave

    def __post_init__(self):
        self.dato = parse(str(self.dato)).date()

    def to_dict(self):
        return {
            "dato": self.dato,
            "vagt_tid": self.vagt_tid,
            "gast": self.gast,
            "opgave": self.opgave.name,
        }

    @staticmethod
    def from_dict(d):
        return Vagt(
            dato=d["dato"],
            vagt_tid=d["vagt_tid"],
            gast=d["gast"],
            opgave=Opgave[d["opgave"]],
        )


class GeorgStage:
    def __init__(self, vagter):
        self._vagter = {}
        for vagt in vagter:
            assert type(vagt) == Vagt
            self._vagter.setdefault(vagt.dato, []).append(vagt)
        datoer = self.get_datoer()
        self.current_dato = datoer[-1] if len(datoer) else None

    def __len__(self):
        """
        returns the number of days set, i.e. distinct **keys** in self._vagter
        """
        return len(self._vagter)

    def get_current_dato(self):
        return self.current_dato

    def set_current_dato(self, dt):
        self.current_dato = dt

    def __getitem__(self, dt):
        dt = parse(str(dt)).date()
        return self._vagter.get(dt) or []

    def __setitem__(self, dt, vagter):
        """
        Set list of Vagter object on a given day
        """
        dt = parse(str(dt)).date()
        self._vagter[dt] = vagter

    def __delitem__(self, dt):
        dt = parse(str(dt)).date()
        del self._vagter[dt]
        if dt == self.current_dato:
            # set new current date
            datoer = self.get_datoer()
            if len(datoer) > 0:
                self.current_dato = datoer[-1]
            else:
                self.current_dato = None

    def get_datoer(self):
        """
        Returns all days that have been set, even empty ones.
        """
        return list(self._vagter.keys())

    def validate(self):
        """
        Validate that the GeorgStage instance is valid.
        """
        return True

    def get_vagter(self, before=None):
        """
        Returns all vagter objects, with optional filtering.
        """
        before = before or parse("9999/9/9")
        before = parse(str(before)).date()
        result = []
        for dato, values in self._vagter.items():
            if before and dato >= before:
                continue
            for vagt in values:
                result.append(vagt)
        return result

    def to_dataframe(self):
        rows = [v.to_dict() for v in self.get_vagter()]
        columns = ["dato", "vagt_tid", "gast", "opgave"]
        if len(rows) > 0:
            return pd.DataFrame(rows)
        else:
            return pd.DataFrame(rows, columns=columns)

    def save(self, filepath):
        df = self.to_dataframe()
        df.to_csv(filepath, index=False)

    @staticmethod
    def load(filepath):
        df = pd.read_csv(filepath)
        return GeorgStage.from_dataframe(df)

    @staticmethod
    def from_dataframe(df):
        vagter = [Vagt.from_dict(row) for idx, row in df.iterrows()]
        return GeorgStage(vagter)
