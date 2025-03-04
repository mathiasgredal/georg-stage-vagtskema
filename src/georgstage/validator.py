"""Validator for the vagtliste"""

from dataclasses import dataclass
from tkinter import messagebox as mb
from typing import Optional

from georgstage.model import HU, Opgave, Vagt, VagtListe, VagtTid


@dataclass
class VagtListConflictError:
    """A conflict in the vagtliste"""

    vagttid: VagtTid
    conflict_a: tuple[Opgave, int]
    conflict_b: tuple[Opgave, int]


def validate_vagt(tid: VagtTid, vagt: Vagt) -> Optional[VagtListConflictError]:
    """Validate a vagt"""
    assigned_opgaver: list[tuple[Opgave, int]] = []

    for opgave, elev_nr in vagt.opgaver.items():
        for assigned_opgave, assigned_elev_nr in assigned_opgaver:
            if elev_nr == assigned_elev_nr:
                return VagtListConflictError(tid, (opgave, elev_nr), (assigned_opgave, assigned_elev_nr))
        assigned_opgaver.append((opgave, elev_nr))

    return None


def validate_vagtliste(vagtliste: VagtListe) -> Optional[VagtListConflictError]:
    """Validate a vagtliste"""
    for tid, vagt in vagtliste.vagter.items():
        error = validate_vagt(tid, vagt)
        if error is not None:
            return error
    return None


def validate_hu(vagtliste: VagtListe, hu: HU) -> Optional[VagtListConflictError]:
    """Validate a hu"""
    for tid, vagt in vagtliste.vagter.items():
        if tid not in [VagtTid.ALL_DAY, VagtTid.T08_12, VagtTid.T12_16]:
            continue

        for opgave, elev_nr in vagt.opgaver.items():
            if opgave == Opgave.VAGTHAVENDE_ELEV:
                continue

            for assignment in hu.assigned:
                if elev_nr != assignment:
                    continue
                return VagtListConflictError(tid, (opgave, elev_nr), (Opgave.HU, assignment))

    return None


def show_validation_error(error: VagtListConflictError) -> None:
    """Show a validation error"""
    mb.showerror(
        'Fejl',
        f'Fejl i vagtliste({error.vagttid.value}) - {error.conflict_a[0].value} og {error.conflict_b[0].value} har samme elev nr. {error.conflict_a[1]}',  # noqa: E501
    )
