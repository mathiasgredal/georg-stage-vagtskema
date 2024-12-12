from georgstage.model import VagtListe, VagtTid, Opgave, Vagt
from pydantic.dataclasses import dataclass

@dataclass
class VagtListConflictError:
    vagttid: VagtTid
    conflict_a: tuple[Opgave, int]
    conflict_b: tuple[Opgave, int]



def validate_vagt(tid: VagtTid,vagt: Vagt) -> VagtListConflictError | None:
    assigned_opgaver: list[tuple[Opgave,int]] = []

    for opgave, elev_nr in vagt.opgaver.items():
        for assigned_opgave, assigned_elev_nr in assigned_opgaver:
            if elev_nr == assigned_elev_nr:
                return VagtListConflictError(tid, (opgave, elev_nr), (assigned_opgave, assigned_elev_nr))
        assigned_opgaver.append((opgave, elev_nr))
    
    return None

def validate_vagtliste(vagtliste: VagtListe) -> VagtListConflictError | None:
    for tid, vagt in vagtliste.vagter.items():
        error = validate_vagt(tid, vagt)
        if error is not None:
            return error
    return None