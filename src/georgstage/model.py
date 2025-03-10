"""Georgstage model"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import Enum, unique
from typing import Any
from uuid import UUID, uuid4

kabys_elev_nrs = [0, 61, 62, 63]


def next_datetime(current: datetime, hour: int, **kwargs: Any) -> datetime:
    """Calculate the next datetime that occurs after the specified hour on the following day.

    This function takes a current datetime and an hour, and returns a new datetime
    object that represents the next occurrence of that hour. If the specified hour
    is already passed for the current day, the function will return the hour for the
    next day.

    Args:
        current (datetime): The current datetime from which to calculate the next occurrence.
        hour (int): The hour (0-23) for which to find the next datetime.
        **kwargs: Additional keyword arguments to pass to the `replace` method of the datetime.

    Returns:
        datetime: A datetime object representing the next occurrence of the specified hour.
    """
    repl = current.replace(hour=hour, **kwargs)
    while repl <= current:
        repl = repl + timedelta(days=1)
    return repl


@unique
class Opgave(Enum):
    """Enumeration of tasks (opgaver) associated with the vagtliste (duty roster).

    Each task represents a specific role or responsibility that can be assigned
    to individuals during their shifts. The tasks include various types of
    watchkeeping and support roles, ensuring a comprehensive coverage of
    duties required during the operation.
    """

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
    NATTEVAGT_A = 'Nattevagt A'
    NATTEVAGT_B = 'Nattevagt B'
    ELEV_VAGTSKIFTE = 'ELEV Vagtskifte'
    HU = 'HU'


@unique
class VagtType(Enum):
    """Enumeration of different types of vagtliste (duty roster).

    This enumeration defines the various types of duty roster that can be used
    in the system. Each type represents a specific pattern or structure of
    duty assignments, which can be used to categorize and organize the vagtliste
    according to the operational requirements and scheduling preferences.
    """

    SOEVAGT = 'Søvagt'
    HAVNEVAGT = 'Havn'
    HOLMEN = 'Holmen'
    HOLMEN_WEEKEND = 'Weekend'


@unique
class VagtSkifte(Enum):
    """Enumeration of shift changes (vagt skifte) for duty rosters.

    This enumeration defines the different types of shift changes that can occur
    within the duty roster system. Each shift change represents a specific
    assignment or transition between different roles during the operational period.
    The defined shifts help in organizing and managing the personnel assignments
    effectively, ensuring that all necessary roles are covered during each shift.
    """

    SKIFTE_1 = 1
    SKIFTE_2 = 2
    SKIFTE_3 = 3


@unique
class VagtTid(Enum):
    """Enumeration of different times of day (vagt tid) for duty rosters."""

    ALL_DAY = 'ALL_DAY'

    # Søvagt
    T08_12 = '08-12'
    T12_15 = '12-15'
    T15_20 = '15-20'
    T20_24 = '20-24'
    T00_04 = '00-04'
    T04_08 = '04-08'

    # Havnevagt
    T12_16 = '12-16'
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
    """A class representing a duty roster (vagt) for a specific time period."""

    vagt_skifte: VagtSkifte
    opgaver: dict[Opgave, int]


@dataclass
class HU:
    """A class representing a HU (HU) for a specific time period."""

    start_date: date
    assigned: list[int]


@dataclass
class VagtListe:
    """A class representing a duty roster (vagtliste) for a specific time period."""

    id: UUID
    vagtperiode_id: UUID
    vagttype: VagtType
    start: datetime
    end: datetime
    note: str
    starting_shift: VagtSkifte
    vagter: dict[VagtTid, Vagt]
    holmen_double_nattevagt: bool = False
    holmen_dækselev_i_kabys: bool = False
    chronological_vagthavende: bool = False
    initial_vagthavende_first_shift: int = 0
    initial_vagthavende_second_shift: int = 0
    initial_vagthavende_third_shift: int = 0

    def __post_init__(self) -> None:
        if isinstance(self.vagttype, str):
            self.vagttype = VagtType(self.vagttype)

        if isinstance(self.starting_shift, int):
            self.starting_shift = VagtSkifte(self.starting_shift)

        self.vagter = {(VagtTid(key) if isinstance(key, str) else key): value for key, value in self.vagter.items()}

        for tid, vagt in self.vagter.items():
            if isinstance(vagt, Vagt):
                continue
            self.vagter[tid] = Vagt(
                VagtSkifte(vagt['vagt_skifte']),
                {Opgave(opgave): elev_nr for opgave, elev_nr in vagt['opgaver'].items()},
            )

    def get_date(self) -> date:
        """Retrieve the effective date of the duty roster (vagtliste).

        The effective date is determined based on the start time of the roster.
        If the start time is 8 AM or later, the date corresponds to the start date.
        If the start time is before 8 AM, the date is adjusted to the previous day.
        """
        return self.start.date() if self.start.hour >= 8 else (self.start - timedelta(days=1)).date()

    def to_string(self) -> str:
        """Convert the vagtliste to a string."""
        if self.vagttype == VagtType.SOEVAGT:
            return f'{self.vagttype.value}: {self.get_date().strftime("%Y-%m-%d")}'
        else:
            return f'{self.vagttype.value}[{self.starting_shift.value}#]:  {self.get_date().strftime("%Y-%m-%d")}'


@dataclass
class VagtPeriode:
    """A class representing a period of duty rosters (vagtperiode)."""

    id: UUID
    vagttype: VagtType
    start: datetime
    end: datetime
    note: str
    starting_shift: VagtSkifte
    holmen_double_nattevagt: bool = False
    holmen_dækselev_i_kabys: bool = False
    chronological_vagthavende: bool = False
    initial_vagthavende_first_shift: int = 0
    initial_vagthavende_second_shift: int = 0
    initial_vagthavende_third_shift: int = 0

    def __post_init__(self) -> None:
        if not self.initial_vagthavende_first_shift == 0:
            if (
                self.initial_vagthavende_first_shift < 1
                or self.initial_vagthavende_first_shift > 20
                or self.initial_vagthavende_first_shift in kabys_elev_nrs
            ):
                raise ValueError(f'Ugyldig vagthavende nr. fra første skifte: {self.initial_vagthavende_first_shift}')

        if not self.initial_vagthavende_second_shift == 0:
            if (
                self.initial_vagthavende_second_shift < 21
                or self.initial_vagthavende_second_shift > 40
                or self.initial_vagthavende_second_shift in kabys_elev_nrs
            ):
                raise ValueError(f'Ugyldig vagthavende nr. fra andet skifte: {self.initial_vagthavende_second_shift}')

        if not self.initial_vagthavende_third_shift == 0:
            if (
                self.initial_vagthavende_third_shift < 41
                or self.initial_vagthavende_third_shift > 60
                or self.initial_vagthavende_third_shift in kabys_elev_nrs
            ):
                raise ValueError(f'Ugyldig vagthavende nr. fra tredje skifte: {self.initial_vagthavende_third_shift}')

        if isinstance(self.vagttype, str):
            self.vagttype = VagtType(self.vagttype)

        if isinstance(self.starting_shift, int):
            self.starting_shift = VagtSkifte(self.starting_shift)

    def to_string(self) -> str:
        """Convert the vagtperiode to a string."""
        return f'{self.vagttype.value}: {self.start.strftime("%Y-%m-%d %H:%M")} - {self.end.strftime("%Y-%m-%d %H:%M")} [{self.starting_shift.value}#] ({self.note})'  # noqa: E501

    def get_vagtliste_stubs(self) -> list[VagtListe]:
        """Generate a list of vagtliste stubs for the vagtperiode.

        This method creates a list of VagtListe objects that represent the duty rosters
        for each day in the specified period. It takes into account the type of vagt
        (e.g., Søvagt, Havn, Holmen, Weekend) and the starting shift for each day.
        """
        vagtliste_dates = []
        current = self.start
        while next_datetime(current, hour=8, minute=0) < self.end:
            next = next_datetime(current, hour=8, minute=0)
            vagtliste_dates.append((current, next))
            current = next

        if len(vagtliste_dates) == 0:
            # The period is less than a day, so we only have one vagtliste
            vagtliste_dates.append((self.start, self.end))
        elif vagtliste_dates[-1][1] != self.end:
            # The last vagtliste is not a full day, we change the end time to the end of the period
            vagtliste_dates.append((vagtliste_dates[-1][1], self.end))

        if self.vagttype == VagtType.SOEVAGT:
            # Each day has the same starting shift
            return [
                VagtListe(
                    uuid4(),
                    self.id,
                    self.vagttype,
                    date[0],
                    date[1],
                    self.note,
                    self.starting_shift,
                    {},
                    self.holmen_double_nattevagt,
                    self.holmen_dækselev_i_kabys,
                    self.chronological_vagthavende,
                    self.initial_vagthavende_first_shift,
                    self.initial_vagthavende_second_shift,
                    self.initial_vagthavende_third_shift,
                )
                for date in vagtliste_dates
            ]
        elif (
            self.vagttype == VagtType.HAVNEVAGT
            or self.vagttype == VagtType.HOLMEN
            or self.vagttype == VagtType.HOLMEN_WEEKEND
        ):
            # Each day has a different starting shift, rotating through the shifts
            current_shift = self.starting_shift.value
            result = []
            for date in vagtliste_dates:
                result.append(
                    VagtListe(
                        uuid4(),
                        self.id,
                        self.vagttype,
                        date[0],
                        date[1],
                        self.note,
                        VagtSkifte(current_shift),
                        {},
                        self.holmen_double_nattevagt,
                        self.holmen_dækselev_i_kabys,
                        self.chronological_vagthavende,
                        self.initial_vagthavende_first_shift,
                        self.initial_vagthavende_second_shift,
                        self.initial_vagthavende_third_shift,
                    )
                )
                if self.vagttype != VagtType.HOLMEN_WEEKEND:
                    current_shift = (current_shift % 3) + 1
            return result
        else:
            raise ValueError(f'Unimplemented VagtType: {self.vagttype}')


@dataclass
class Afmønstring:
    """A class representing an afmønstring (duty roster de-enrollment)."""

    id: UUID
    elev_nr: int
    name: str
    start_date: date
    end_date: date

    def to_string(self) -> str:
        """Convert the afmønstring to a string."""
        return f'{self.name}[nr. {self.elev_nr}]:  {self.start_date.strftime("%Y-%m-%d")} - {self.end_date.strftime("%Y-%m-%d")}'  # noqa: E501
