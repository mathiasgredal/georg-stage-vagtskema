from datetime import datetime, timedelta
from enum import Enum, unique

from pydantic.dataclasses import dataclass
from uuid import UUID, uuid4


def next_datetime(current: datetime, hour: int, **kwargs) -> datetime:
    repl = current.replace(hour=hour, **kwargs)
    while repl <= current:
        repl = repl + timedelta(days=1)
    return repl


@unique
class Opgave(Enum):
    VAGTHAVENDE_ELEV = 'Vagthavende ELEV'
    ORDONNANS = 'Ordonnans'
    UDKIG = 'Udkig'
    RADIOVAGT = 'Radiovagt'
    RORGAENGER = 'Rorgænger'
    UDSAETNINGSGAST_A = 'Udsætningsgast A'
    UDSAETNINGSGAST_B = 'Udsætningsgast B'
    UDSAETNINGSGAST_C = 'Udsætningsgast C'
    UDSAETNINGSGAST_D = 'Udsætningsgast D'
    UDSAETNINGSGAST_E = 'Udsætningsgast E'
    PEJLEGAST_A = 'Pejlegast A'
    PEJLEGAST_B = 'Pejlagast B'
    DAEKSELEV_I_KABYS = 'Dækselev i kabys'
    LANDGANGSVAGT_A = 'Landgangsvagt A'
    LANDGANGSVAGT_B = 'Landgangsvagt B'
    NATTEVAGT = 'NATTEVAGT'
    ELEV_VAGTSKIFTE = 'ELEV Vagtskifte'


@unique
class VagtType(Enum):
    SOEVAGT = 'Søvagt'
    HAVNEVAGT = 'Havnevagt'
    HOLMEN = 'Holmen'


@unique
class VagtSkifte(Enum):
    SKIFTE_1 = 1
    SKIFTE_2 = 2
    SKIFTE_3 = 3


@unique
class VagtTid(Enum):
    ALL_DAY = 'ALL_DAY'

    # Søvagt
    T08_12 = '08-12'
    T12_15 = '12-15'
    T15_20 = '15-20'
    T20_24 = '20-24'
    T00_04 = '00-04'
    T04_08 = '04-08'

    # Havnevagt
    T08_10 = '08-10'
    T10_12 = '10-12'
    T12_14 = '12-14'
    T14_16 = '14-16'
    T16_18 = '16-18'
    T18_20 = '18-20'
    T20_22 = '20-22'
    T22_00 = '22-24'
    T00_02 = '00-02'
    T02_04 = '02-04'
    T04_06 = '04-06'
    T06_08 = '06-08'


@dataclass
class Vagt:
    vagt_skifte: VagtSkifte
    opgaver: dict[Opgave, int]


@dataclass
class VagtListe:
    id: UUID
    vagtperiode_id: UUID
    vagttype: VagtType
    start: datetime
    end: datetime
    note: str
    starting_shift: VagtSkifte
    vagter: dict[VagtTid, Vagt]


@dataclass
class VagtPeriode:
    id: UUID
    vagttype: VagtType
    start: datetime
    end: datetime
    note: str
    starting_shift: VagtSkifte

    def to_string(self) -> str:
        return f"{self.vagttype.value}: {self.start.strftime('%Y-%m-%d %H:%M')} - {self.end.strftime('%Y-%m-%d %H:%M')} [{self.starting_shift.value}#] ({self.note})"

    def get_vagtliste_stubs(self) -> list[VagtListe]:
        vagtliste_dates = []
        current = self.start
        while next_datetime(current, hour=8, minute=0) < self.end:
            next = next_datetime(current, hour=8, minute=0)
            vagtliste_dates.append((current, next))
            current = next

        if vagtliste_dates[-1][1] != self.end:
            vagtliste_dates.append((vagtliste_dates[-1][1], self.end))

        if self.vagttype == VagtType.SOEVAGT:
            return [
                VagtListe(uuid4(), self.id, self.vagttype, date[0], date[1], self.note, self.starting_shift, {})
                for date in vagtliste_dates
            ]
        elif self.vagttype == VagtType.HAVNEVAGT:
            current_shift = self.starting_shift.value
            result = []
            for date in vagtliste_dates:
                result.append(
                    VagtListe(
                        uuid4(), self.id, self.vagttype, date[0], date[1], self.note, VagtSkifte(current_shift), {}
                    )
                )
                current_shift = (current_shift % 3) + 1
            return result
        else:
            raise ValueError(f'Unimplemented VagtType: {self.vagttype}')


# Registry
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

# Enlistments:
# Attributes:
#   - Vagt
#   - Opgave
#   - Tid
# Functions:
#   - GetTraineeNumber() -> int


# Flows
# - Create a VagtPeriode
# - Create a set of VagtListe from a VagtPeriode
