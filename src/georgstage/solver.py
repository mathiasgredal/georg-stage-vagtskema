from georgstage.model import VagtListe, VagtTid, Vagt, Opgave
from typing import Optional
from datetime import datetime, timedelta
from georgstage.util import EnhancedJSONEncoder
import json
from typing import Any, cast
import random

dummy_vls: list[VagtListe] = [
    VagtListe("Søvagt", datetime.fromisoformat("2024-12-02 10:00"),datetime.fromisoformat("2024-12-04 10:00"),"", 3, {}),
    VagtListe("Søvagt", datetime.fromisoformat("2024-12-04 10:00"),datetime.fromisoformat("2024-12-06 01:00"),"", 2, {
        VagtTid.T08_12: Vagt(2, {
            Opgave.VAGTHAVENDE_ELEV: 24
        })
    })
]

def get_skifte_from_elev_nr(elev_nr: int) -> int:
    if elev_nr >= 1 and elev_nr <= 20:
        return 1
    if elev_nr >= 21 and elev_nr <= 40:
        return 2
    if elev_nr >= 41 and elev_nr <= 60:
        return 3
    # raise ValueError(f"Number {elev_nr} must be between 1 and 63")

def is_nattevagt(vagttid: VagtTid):
    return vagttid in [VagtTid.T20_24, VagtTid.T00_04, VagtTid.T04_08]

def is_dagsvagt(vagttid: VagtTid):
    return vagttid in [VagtTid.T08_12, VagtTid.T12_15, VagtTid.T15_20]

def generate_vagttider(start: datetime, end: datetime) -> list[VagtTid]:
    next_day = start+timedelta(days=1)
    potential_vagttider = {
        VagtTid.T08_12: (start.replace(hour=8,minute=0), start.replace(hour=12,minute=0)),
        VagtTid.T12_15: (start.replace(hour=12,minute=0), start.replace(hour=15,minute=0)),
        VagtTid.T15_20: (start.replace(hour=15,minute=0),start.replace(hour=20,minute=0)),
        VagtTid.T20_24: (start.replace(hour=20,minute=0), start.replace(hour=23,minute=59)),
        VagtTid.T00_04: (next_day.replace(hour=0,minute=0), next_day.replace(hour=4,minute=0)),
        VagtTid.T04_08: (next_day.replace(hour=4,minute=0), next_day.replace(hour=8,minute=0))
    }

    filtered_vagttider: list[VagtTid] = []

    for vagttid, (vagttid_start, vagttid_end) in potential_vagttider.items():
        if vagttid_end < start:
            continue
        if vagttid_start > end:
            continue
        filtered_vagttider.append(vagttid)

    return filtered_vagttider


def autofill_vagt(skifte: int, time: VagtTid, vl: VagtListe, all_vls: list[VagtListe]) -> Vagt:
    vagt = Vagt(skifte, {})
    stats = count_vagt_stats(all_vls)
    skifte_stats = filter_by_skifte(skifte, stats)

    # TODO: Instead of making some numbers completely unavailable, we should just weight them so they are less likely to be picked
    unavailable_numbers: list[int] = []

    print(filter_by_opgave(Opgave.VAGTHAVENDE_ELEV, skifte_stats))
    
    vagt.opgaver[Opgave.VAGTHAVENDE_ELEV] = pick_least(unavailable_numbers, filter_by_opgave(Opgave.VAGTHAVENDE_ELEV, skifte_stats))
    unavailable_numbers.append(vagt.opgaver[Opgave.VAGTHAVENDE_ELEV])

    # if nattevagt, find dagsvagter and add to unavailable_numbers
    fysiske_vagter = [Opgave.ORDONNANS, Opgave.UDKIG, Opgave.RADIOVAGT, Opgave.RORGAENGER]

    # Subtract start_date by 1 day, match all vls, to find that day
    vl_one_day_ago: Optional[VagtListe] = None
    vl_two_days_ago: Optional[VagtListe] = None
    for _vl in all_vls:
        if (vl.start - timedelta(days=1)).date() == _vl.start.date():
            vl_one_day_ago = _vl
        if (vl.start - timedelta(days=2)).date() == _vl.start.date():
            vl_two_days_ago = _vl

    prev_vagter: list[int] = []
    for _vl in [vl, vl_one_day_ago]:
        if _vl is None:
            continue
        for tid, _vagt in _vl.vagter.items():
            for opgave, elev_nr in _vagt.opgaver.items():
                if opgave not in fysiske_vagter:
                    continue
                prev_vagter.append(elev_nr)

    if vl_two_days_ago is not None:
        for _tid, _vagt in vl_two_days_ago.vagter.items():
            for opgave, elev_nr in _vagt.opgaver.items():
                if opgave not in fysiske_vagter:
                    continue
                if is_dagsvagt(_tid) and is_nattevagt(time):
                    prev_vagter.append(elev_nr)
                if is_nattevagt(_tid) and is_dagsvagt(time):
                    prev_vagter.append(elev_nr)

    for fysisk_vagt in fysiske_vagter:
        vagt.opgaver[fysisk_vagt] = pick_least([*unavailable_numbers, *prev_vagter], filter_by_opgave(fysisk_vagt, skifte_stats))
        unavailable_numbers.append(vagt.opgaver[fysisk_vagt])

    udsætningsgast_opgaver = [Opgave.UDSAETNINGSGAST_A, Opgave.UDSAETNINGSGAST_B, Opgave.UDSAETNINGSGAST_C, Opgave.UDSAETNINGSGAST_D, Opgave.UDSAETNINGSGAST_E]
    for opgave in udsætningsgast_opgaver:
        vagt.opgaver[opgave] = pick_least(unavailable_numbers, filter_by_opgave(opgave, skifte_stats))
        unavailable_numbers.append(vagt.opgaver[opgave])

    if (time in [VagtTid.T04_08, VagtTid.T08_12, VagtTid.T12_15, VagtTid.T15_20]):
        vagt.opgaver[Opgave.DAEKSELEV_I_KABYS] = pick_least(unavailable_numbers, filter_by_opgave(Opgave.DAEKSELEV_I_KABYS, skifte_stats))
        unavailable_numbers.append(vagt.opgaver[Opgave.DAEKSELEV_I_KABYS])
    
    if time == VagtTid.T15_20:
        # If vl one days ago is None or the shift for that time is not the same, create 2 random numbers
        def create_2_pejlegasts():
            vagt.opgaver[Opgave.PEJLEGAST_A] = pick_least(unavailable_numbers, filter_by_opgave(Opgave.PEJLEGAST_A, skifte_stats))
            unavailable_numbers.append(vagt.opgaver[Opgave.PEJLEGAST_A])

            vagt.opgaver[Opgave.PEJLEGAST_B] = pick_least(unavailable_numbers, filter_by_opgave(Opgave.PEJLEGAST_B, skifte_stats))
            unavailable_numbers.append(vagt.opgaver[Opgave.PEJLEGAST_B])

        if vl_one_day_ago is not None:
            if vl_one_day_ago.starting_shift != vl.starting_shift:
                create_2_pejlegasts()
            if time in vl_one_day_ago.vagter and Opgave.PEJLEGAST_B in vl_one_day_ago.vagter[time].opgaver:
                vagt.opgaver[Opgave.PEJLEGAST_A] = vl_one_day_ago.vagter[time].opgaver[Opgave.PEJLEGAST_B]
                unavailable_numbers.append(vagt.opgaver[Opgave.PEJLEGAST_A])
                vagt.opgaver[Opgave.PEJLEGAST_B] = pick_least(unavailable_numbers, filter_by_opgave(Opgave.PEJLEGAST_B, skifte_stats))
                unavailable_numbers.append(vagt.opgaver[Opgave.PEJLEGAST_B])
            else:
                create_2_pejlegasts()
        else:
            create_2_pejlegasts()

    return vagt


def filter_by_opgave(opgave: Opgave, stats: dict[tuple[Opgave,int], int]) -> dict[tuple[Opgave,int], int]:
    filtered_stats: dict[tuple[Opgave,int], int] = {}

    for (opg, elev_nr), antal in stats.items():
        if opg != opgave:
            continue
        filtered_stats[(opg, elev_nr)] = antal
    
    return filtered_stats

def filter_by_skifte(skifte: int, stats: dict[tuple[Opgave,int], int]) -> dict[tuple[Opgave,int], int]:
    filtered_stats: dict[tuple[Opgave,int], int] = {}
    
    for (opg, elev_nr), antal in stats.items():
        if get_skifte_from_elev_nr(elev_nr) != skifte:
            continue
        filtered_stats[(opg, elev_nr)] = antal
    
    return filtered_stats

def pick_least(unavailable_numbers: list[int], stats: dict[tuple[Opgave,int], int]) -> int:
    # TODO: There might be a slight bias in this algorithm, 
    #       where similar groups are always assigned together
    elev_nr_and_count: list[tuple[int, int]] = []

    for (_, elev_nr), antal in stats.items():
        if elev_nr in unavailable_numbers:
            continue
        elev_nr_and_count.append((elev_nr, antal))

    elev_nr_and_count.sort(key=lambda tup: tup[1])
    if len(elev_nr_and_count) == 0:
        print(f"Could not find an available number, given these reserved numbers: {unavailable_numbers}")
        print(f"The associated stats: {stats}")
    least_count = elev_nr_and_count[0][1]
    # TODO: Add a random inclusion factor here
    all_least_elev_nr = [elev_nr for elev_nr, count in elev_nr_and_count if count==least_count]
    return random.choice(all_least_elev_nr)

def count_vagt_stats(all_vls: list[VagtListe]) -> dict[tuple[Opgave,int], int]:
    vagt_stats: dict[tuple[Opgave,int], int] = {}

    for i in range(63):
        if i in [9, 61, 62, 63]:
            continue

        for opg in Opgave._member_map_.values():
            vagt_stats[(cast(Any, opg), i)] = 0


    for vagtliste in all_vls:
        for _, vagt_col in vagtliste.vagter.items():
            for opg, elev_nr in vagt_col.opgaver.items():
                vagt_stats[(opg, elev_nr)] += 1
    
    return vagt_stats


def autofill_vagtliste(vl: VagtListe, all_vls: list[VagtListe]) -> Optional[str]:
    vagttider: list[VagtTid] = generate_vagttider(vl.start, vl.end)
    skifter: dict[VagtTid, int] = {}

    # Compute the shift for each vagt using modulo
    for index, vagttid in enumerate(VagtTid._value2member_map_):
        skifter[vagttid] = (index + vl.starting_shift-1) % 3 + 1

    for vagttid in vagttider:
        skifte = skifter[vagttid.value]
        print(f"Autofilling {vagttid.value} for {skifte}#...")
        vl.vagter[vagttid.value] = autofill_vagt(skifte, vagttid, vl, all_vls)
    return None


# autofill_vagtliste(dummy_vls[0], dummy_vls)

datetime.fromisoformat("2024-12-02 10:00").replace(hour=8,minute=0)
datetime.fromisoformat("2024-12-02 10:00").replace(hour=12,minute=0)
some_date = datetime.fromisoformat("2024-12-02 10:00")

some_date + timedelta(days=1)

# for each vagttid
#   Check vagttid is within bounds
#   for each opgave
#       Vagthavende elev -> Take a random person from a team among those in the team who has been vagthavende elev the least
#       Fysisk vagt ->
#           Filter eligble: already assigned, specific skifte, sidste dagsvagt/nattevagt
#           Pick random least chosen number
#       MOB trainee ->
#           Filter eligble: already assigned, specific skifte
#           Pick random least chosen number
#       