from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum, unique


def next_datetime(current: datetime, hour: int, **kwargs) -> datetime:
    repl = current.replace(hour=hour, **kwargs)
    while repl <= current:
        repl = repl + timedelta(days=1)
    return repl


@unique
class Opgave(str, Enum):
    VAGTHAVENDE_ELEV = "Vagthavende ELEV"
    ORDONNANS = "Ordonnans"
    UDKIG = "Udkig"
    RADIOVAGT = "Radiovagt"
    RORGAENGER = "Rorgænger"
    UDSAETNINGSGAST_A = "Udsætningsgast A"
    UDSAETNINGSGAST_B = "Udsætningsgast B"
    UDSAETNINGSGAST_C = "Udsætningsgast C"
    UDSAETNINGSGAST_D = "Udsætningsgast D"
    UDSAETNINGSGAST_E = "Udsætningsgast E"
    PEJLEGAST_A = "Pejlegast A"
    PEJLEGAST_B = "Pejlagast B"
    DAEKSELEV_I_KABYS = "Dækselev i kabys"


class VagtTid(Enum):
    T08_12 = "08-12"
    T12_15 = "12-15"
    T15_20 = "15-20"
    T20_24 = "20-24"
    T00_04 = "00-04"
    T04_08 = "04-08"


@dataclass
class Vagt:
    vagt_skifte: int
    opgaver: dict[Opgave, int]


@dataclass
class VagtListe:
    vagttype: str
    start: datetime
    end: datetime
    note: str
    starting_shift: int
    vagter: dict[VagtTid, Vagt]

    # def get_vagt(tid: VagtTid, opgave: Opgave) -> int: ...


@dataclass
class VagtPeriode:
    vagttype: str
    start: datetime
    end: datetime
    note: str
    starting_shift: int

    def to_string(self):
        return f"{self.vagttype}: {self.start.strftime('%Y-%m-%d %H:%M')} - {self.end.strftime('%Y-%m-%d %H:%M')} [{self.starting_shift}#] ({self.note})"

    def get_vagtliste_stubs(self) -> list[VagtListe]:
        vagtliste_dates = []
        current = self.start
        while next_datetime(current, hour=8, minute=0) < self.end:
            next = next_datetime(current, hour=8, minute=0)
            vagtliste_dates.append((current, next))
            current = next

        if vagtliste_dates[-1][1] != self.end:
            vagtliste_dates.append((vagtliste_dates[-1][1], self.end))

        return [
            VagtListe(
                self.vagttype, date[0], date[1], self.note, self.starting_shift, {}
            )
            for date in vagtliste_dates
        ]
        # print(json.dumps(vagtliste_dates, cls=EnhancedJSONEncoder))


# VagtDAO
# Attributes:
#   - Vagtperioder
#   - Vagtliste

# Vagtperiode:
# Attributes:
#   - Type
#   - Start
#   - End
#   - Shift
# Functions:
#   - getVagtlisteDates() -> list[date, type]

# Vagtliste:
# Attributes:
#   -
