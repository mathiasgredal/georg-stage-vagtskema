"""Solver for georgstage"""

import collections
import logging
import random
from datetime import date, datetime, timedelta
from tkinter import messagebox as mb
from typing import TYPE_CHECKING, Any, Optional, cast

from georgstage.model import Opgave, Vagt, VagtListe, VagtSkifte, VagtTid, VagtType, kabys_elev_nrs

if TYPE_CHECKING:
    from georgstage.registry import Registry


def get_skifte_from_elev_nr(elev_nr: int) -> VagtSkifte:
    """Get the skifte from the elev nr"""
    if elev_nr >= 1 and elev_nr <= 20:
        return VagtSkifte.SKIFTE_1
    if elev_nr >= 21 and elev_nr <= 40:
        return VagtSkifte.SKIFTE_2
    if elev_nr >= 41 and elev_nr <= 60:
        return VagtSkifte.SKIFTE_3
    raise ValueError(f'Number {elev_nr} must be between 1 and 63')


def is_nattevagt(vagttid: VagtTid) -> bool:
    """Check if the vagttid is a nattevagt"""
    return vagttid in [
        # Søvagt
        VagtTid.T20_24,
        VagtTid.T00_04,
        VagtTid.T04_08,
        # Havnevagt
        VagtTid.T22_00,
        VagtTid.T00_02,
        VagtTid.T02_04,
        VagtTid.T04_06,
        VagtTid.T06_08,
    ]


def is_dagsvagt(vagttid: VagtTid) -> bool:
    """Check if the vagttid is a dagsvagt"""
    return vagttid in [
        # Søvagt
        VagtTid.T08_12,
        VagtTid.T12_15,
        VagtTid.T15_20,
        # Havnevagt
        VagtTid.T12_16,
        VagtTid.T16_18,
        VagtTid.T18_20,
        VagtTid.T20_22,
    ]


def generate_søvagt_vagttider(start: datetime, end: datetime) -> list[VagtTid]:
    """Generate the søvagt vagttider"""
    next_day = (start + timedelta(days=1)) if start.hour >= 8 else start
    potential_vagttider = {
        VagtTid.T08_12: (start.replace(hour=8, minute=1), start.replace(hour=12, minute=0)),
        VagtTid.T12_15: (start.replace(hour=12, minute=0), start.replace(hour=15, minute=0)),
        VagtTid.T15_20: (start.replace(hour=15, minute=0), start.replace(hour=20, minute=0)),
        VagtTid.T20_24: (start.replace(hour=20, minute=0), start.replace(hour=23, minute=59)),
        VagtTid.T00_04: (next_day.replace(hour=0, minute=0), next_day.replace(hour=4, minute=0)),
        VagtTid.T04_08: (next_day.replace(hour=4, minute=0), next_day.replace(hour=8, minute=0)),
    }

    # Subtract 1 second from all the potential end times
    for vagttid, (vagttid_start, vagttid_end) in potential_vagttider.items():
        potential_vagttider[vagttid] = (vagttid_start, vagttid_end - timedelta(seconds=1))

    filtered_vagttider: list[VagtTid] = []

    for vagttid, (vagttid_start, vagttid_end) in potential_vagttider.items():
        if vagttid_end < start:
            continue
        if vagttid_start > end:
            continue
        filtered_vagttider.append(vagttid)

    return filtered_vagttider


def generate_havnevagt_vagttider(start: datetime, end: datetime) -> list[VagtTid]:
    """Generate the havnevagt vagttider"""
    next_day = (start + timedelta(days=1)) if start.hour >= 8 else start
    potential_vagttider = {
        VagtTid.T08_12: (start.replace(hour=8, minute=1), start.replace(hour=12, minute=0)),
        VagtTid.T12_16: (start.replace(hour=12, minute=0), start.replace(hour=16, minute=0)),
        VagtTid.T16_18: (start.replace(hour=16, minute=0), start.replace(hour=18, minute=0)),
        VagtTid.T18_20: (start.replace(hour=18, minute=0), start.replace(hour=20, minute=0)),
        VagtTid.T20_22: (start.replace(hour=20, minute=0), start.replace(hour=22, minute=0)),
        VagtTid.T22_00: (start.replace(hour=22, minute=0), start.replace(hour=23, minute=59)),
        VagtTid.T00_02: (next_day.replace(hour=0, minute=0), next_day.replace(hour=2, minute=0)),
        VagtTid.T02_04: (next_day.replace(hour=2, minute=0), next_day.replace(hour=4, minute=0)),
        VagtTid.T04_06: (next_day.replace(hour=4, minute=0), next_day.replace(hour=6, minute=0)),
        VagtTid.T06_08: (next_day.replace(hour=6, minute=0), next_day.replace(hour=8, minute=0)),
    }

    # Subtract 1 second from all the potential end times
    for vagttid, (vagttid_start, vagttid_end) in potential_vagttider.items():
        potential_vagttider[vagttid] = (vagttid_start, vagttid_end - timedelta(seconds=1))

    filtered_vagttider: list[VagtTid] = [VagtTid.ALL_DAY]

    for vagttid, (vagttid_start, vagttid_end) in potential_vagttider.items():
        if vagttid_end < start:
            continue
        if vagttid_start > end:
            continue
        filtered_vagttider.append(vagttid)

    return filtered_vagttider


def separate_havnevagt_dagsvagter_nattevagter(vagttider: list[VagtTid]) -> tuple[list[VagtTid], list[VagtTid]]:
    """Separate the havnevagt dagsvagter and nattevagter"""
    dagsvagter: list[VagtTid] = []
    nattevagter: list[VagtTid] = []

    for vagttid in vagttider:
        if is_dagsvagt(vagttid):
            dagsvagter.append(vagttid)
        if is_nattevagt(vagttid):
            nattevagter.append(vagttid)

    return dagsvagter, nattevagter


def generate_holmen_vagttider(start: datetime, end: datetime) -> list[VagtTid]:
    """Generate the holmen vagttider"""
    next_day = (start + timedelta(days=1)) if start.hour >= 8 else start
    potential_vagttider = {
        VagtTid.T22_00: (start.replace(hour=22, minute=0), start.replace(hour=23, minute=59)),
        VagtTid.T00_02: (next_day.replace(hour=0, minute=0), next_day.replace(hour=2, minute=0)),
        VagtTid.T02_04: (next_day.replace(hour=2, minute=0), next_day.replace(hour=4, minute=0)),
        VagtTid.T04_06: (next_day.replace(hour=4, minute=0), next_day.replace(hour=6, minute=0)),
        VagtTid.T06_08: (next_day.replace(hour=6, minute=0), next_day.replace(hour=8, minute=0)),
    }

    # Subtract 1 second from all the potential end times
    for vagttid, (vagttid_start, vagttid_end) in potential_vagttider.items():
        potential_vagttider[vagttid] = (vagttid_start, vagttid_end - timedelta(seconds=1))

    filtered_vagttider: list[VagtTid] = [VagtTid.ALL_DAY]

    for vagttid, (vagttid_start, vagttid_end) in potential_vagttider.items():
        if vagttid_end < start:
            continue
        if vagttid_start > end:
            continue
        filtered_vagttider.append(vagttid)

    return filtered_vagttider


def get_last_vagthavende_from_skifte(
    time: VagtTid,
    current_vl: VagtListe,
    registry: 'Registry',
    skifte: VagtSkifte,
) -> int:
    """Get the last vagthavende from the skifte"""
    initial_vagthavende: dict[VagtSkifte, int] = {
        VagtSkifte.SKIFTE_1: current_vl.initial_vagthavende_first_shift,
        VagtSkifte.SKIFTE_2: current_vl.initial_vagthavende_second_shift,
        VagtSkifte.SKIFTE_3: current_vl.initial_vagthavende_third_shift,
    }

    # Check if there is a earlier time in the same vl
    for tid, vagt in current_vl.vagter.items():
        if tid == time:
            continue

        if vagt.vagt_skifte != skifte:
            continue

        if Opgave.VAGTHAVENDE_ELEV in vagt.opgaver:
            return vagt.opgaver[Opgave.VAGTHAVENDE_ELEV]

    last_vl: Optional[VagtListe] = None
    # Find the vl which is closest to the current vl, but before it
    for vl in registry.vagtlister:
        if vl.start >= current_vl.start:
            continue

        if initial_vagthavende[skifte] != 0 and vl.vagtperiode_id != current_vl.vagtperiode_id:
            continue

        # Check if a vagthavende from this skifte is assigned in the vl
        has_vagthavende = False
        for _, vagt in vl.vagter.items():
            if vagt.vagt_skifte == skifte and Opgave.VAGTHAVENDE_ELEV in vagt.opgaver:
                has_vagthavende = True
                break

        if not has_vagthavende:
            continue

        if last_vl is None or vl.start > last_vl.start:
            last_vl = vl

    if last_vl is None:
        return -1

    # Find all the vagthaverne from the last vl from the given skifte
    vagthavende: dict[VagtTid, int] = {}
    for tid, vagt in last_vl.vagter.items():
        if vagt.vagt_skifte == skifte and Opgave.VAGTHAVENDE_ELEV in vagt.opgaver:
            vagthavende[tid] = vagt.opgaver[Opgave.VAGTHAVENDE_ELEV]

    if VagtTid.ALL_DAY in vagthavende:
        return vagthavende[VagtTid.ALL_DAY]

    for tid in [VagtTid.T20_24, VagtTid.T00_04, VagtTid.T04_08]:
        if tid in vagthavende:
            return vagthavende[tid]

    for tid in [VagtTid.T08_12, VagtTid.T12_15, VagtTid.T15_20]:
        if tid in vagthavende:
            return vagthavende[tid]

    return -1

def get_last_pejlegast_b_from_skifte(
    time: VagtTid,
    current_vl: VagtListe,
    registry: 'Registry',
    skifte: VagtSkifte,
) -> int:
    """Get the last pejlegast b from the skifte, or negative if none"""
    
    # Check if there is a earlier time in the same vl
    for tid, vagt in current_vl.vagter.items():
        if tid == time:
            continue

        if vagt.vagt_skifte != skifte:
            continue

        if Opgave.PEJLEGAST_B in vagt.opgaver:
            return vagt.opgaver[Opgave.PEJLEGAST_B]

    last_vl: Optional[VagtListe] = None
    # Find the vl which is closest to the current vl, but before it
    for vl in registry.vagtlister:
        if vl.start >= current_vl.start:
            continue

        # Check if a pejlegast b from this skifte is assigned in the vl
        has_pejlegast_b = False
        for _, vagt in vl.vagter.items():
            if vagt.vagt_skifte == skifte and Opgave.PEJLEGAST_B in vagt.opgaver:
                has_pejlegast_b = True
                break

        if not has_pejlegast_b:
            continue

        if last_vl is None or vl.start > last_vl.start:
            last_vl = vl

    if last_vl is None:
        return -1

    # Find all the pejlegast b from the last vl from the given skifte
    pejlegast_b: dict[VagtTid, int] = {}
    for tid, vagt in last_vl.vagter.items():
        if vagt.vagt_skifte == skifte and Opgave.PEJLEGAST_B in vagt.opgaver:
            pejlegast_b[tid] = vagt.opgaver[Opgave.PEJLEGAST_B]

    if VagtTid.ALL_DAY in pejlegast_b:
        return pejlegast_b[VagtTid.ALL_DAY]

    for tid in [VagtTid.T20_24, VagtTid.T00_04, VagtTid.T04_08]:
        if tid in pejlegast_b:
            return pejlegast_b[tid]

    for tid in [VagtTid.T08_12, VagtTid.T12_15, VagtTid.T15_20]:
        if tid in pejlegast_b:
            return pejlegast_b[tid]

    return -1

def get_chronological_vagthavende(
    time: VagtTid,
    vl: VagtListe,
    registry: 'Registry',
    skifte: VagtSkifte,
    unavailable_numbers: list[int],
) -> int:
    """Get the chronological vagthavende"""
    vagthavende = get_last_vagthavende_from_skifte(
        time,
        vl,
        registry,
        skifte,
    )

    if vagthavende == -1:
        if skifte == VagtSkifte.SKIFTE_1:
            vagthavende = 1 if vl.initial_vagthavende_first_shift == 0 else vl.initial_vagthavende_first_shift
        if skifte == VagtSkifte.SKIFTE_2:
            vagthavende = 21 if vl.initial_vagthavende_second_shift == 0 else vl.initial_vagthavende_second_shift
        if skifte == VagtSkifte.SKIFTE_3:
            vagthavende = 41 if vl.initial_vagthavende_third_shift == 0 else vl.initial_vagthavende_third_shift
        return vagthavende

    while True:
        vagthavende = get_next_vagthavende(vagthavende, skifte)
        if vagthavende not in unavailable_numbers:
            break

    return vagthavende


def get_next_vagthavende(elev_nr: int, skifte: VagtSkifte) -> int:
    """Get the next vagthavende"""
    if skifte == VagtSkifte.SKIFTE_1 and elev_nr == 20:
        return 1
    if skifte == VagtSkifte.SKIFTE_2 and elev_nr == 40:
        return 21
    if skifte == VagtSkifte.SKIFTE_3 and elev_nr == 60:
        return 41
    next_elev_nr = elev_nr + 1
    if next_elev_nr in kabys_elev_nrs:
        return get_next_vagthavende(next_elev_nr, skifte)
    return next_elev_nr


def autofill_vagt(skifte: VagtSkifte, time: VagtTid, vl: VagtListe, registry: 'Registry', ude_nr: list[int]) -> Vagt:
    """Autofill a vagt"""
    vagt = Vagt(skifte, {}) if time not in vl.vagter else vl.vagter[time]
    stats = count_vagt_stats(registry.vagtlister)
    skifte_stats = filter_by_skifte(skifte, stats)

    unavailable_numbers: list[int] = [*ude_nr]

    # Add afmønstringer to unavailable numbers
    for afmønstring in registry.afmønstringer:
        if afmønstring.start_date <= vl.start.date() and afmønstring.end_date >= vl.end.date():
            unavailable_numbers.append(afmønstring.elev_nr)

    # Add existing vagter to unavailable numbers
    for _, nr in vagt.opgaver.items():
        unavailable_numbers.append(nr)

    # Subtract start_date by 1 day, match all vls, to find that day
    vl_one_day_ago: Optional[VagtListe] = None
    for _vl in registry.vagtlister:
        if (vl.start - timedelta(days=1)).date() == _vl.start.date():
            vl_one_day_ago = _vl

    if Opgave.VAGTHAVENDE_ELEV not in vagt.opgaver:
        if vl.chronological_vagthavende:
            vagt.opgaver[Opgave.VAGTHAVENDE_ELEV] = get_chronological_vagthavende(
                time, vl, registry, skifte, unavailable_numbers
            )
        else:
            last_vagthavende_elev = get_last_vagthavende_from_skifte(
                time,
                vl,
                registry,
                skifte,
            )

            vagt.opgaver[Opgave.VAGTHAVENDE_ELEV] = pick_least(
                [last_vagthavende_elev, *unavailable_numbers], filter_by_opgave(Opgave.VAGTHAVENDE_ELEV, skifte_stats)
            )
    unavailable_numbers.append(vagt.opgaver[Opgave.VAGTHAVENDE_ELEV])

    # If on this day, another vl exists on that same day, which contains an ALL_DAY DÆKSELEV_I_KABYS,
    # and the skifte for both is the same, reuse the DÆKSELEV_I_KABYS from the other vl
    dækselev_i_kabys = 0
    for _vl in registry.vagtlister:
        if vl.start.date() != _vl.start.date():
            continue

        if skifte != _vl.starting_shift:
            continue

        if _vl.vagttype not in [VagtType.HAVNEVAGT, VagtType.HOLMEN, VagtType.HOLMEN_WEEKEND]:
            continue

        if VagtTid.ALL_DAY not in _vl.vagter or Opgave.DAEKSELEV_I_KABYS not in _vl.vagter[VagtTid.ALL_DAY].opgaver:
            continue

        if _vl.vagter[VagtTid.ALL_DAY].opgaver[Opgave.DAEKSELEV_I_KABYS] in unavailable_numbers:
            continue

        dækselev_i_kabys = _vl.vagter[VagtTid.ALL_DAY].opgaver[Opgave.DAEKSELEV_I_KABYS]
        unavailable_numbers.append(dækselev_i_kabys)

    # Reserve the last pejlegast b from the skifte
    last_pejlegast_b = get_last_pejlegast_b_from_skifte(
        time,
        vl,
        registry,
        skifte,
    )
    if last_pejlegast_b != -1:
        if last_pejlegast_b in unavailable_numbers:
            last_pejlegast_b = -1
        else:
            unavailable_numbers.append(last_pejlegast_b)
        
    # if nattevagt, find dagsvagter and add to unavailable_numbers
    fysiske_vagter = [Opgave.ORDONNANS, Opgave.UDKIG, Opgave.RADIOVAGT, Opgave.RORGAENGER]

    fysiske_vagter_current: list[int] = []
    for _vl in [vl, vl_one_day_ago]:
        for _, _vagt in vl.vagter.items():
            for opgave, elev_nr in _vagt.opgaver.items():
                if opgave not in fysiske_vagter:
                    continue
                fysiske_vagter_current.append(elev_nr)

    for fysisk_vagt in fysiske_vagter:
        for fysisk_vagt in fysiske_vagter:
            if fysisk_vagt not in vagt.opgaver:
                vagt.opgaver[fysisk_vagt] = pick_most_days_since(
                    [*unavailable_numbers, *fysiske_vagter_current],
                    time,
                    skifte,
                    vl.get_date(),
                    registry,
                )
                if vagt.opgaver[fysisk_vagt] is None:
                    vagt.opgaver[fysisk_vagt] = pick_least(
                        [*unavailable_numbers, *fysiske_vagter_current], filter_by_opgave(fysisk_vagt, skifte_stats)
                    )
            unavailable_numbers.append(vagt.opgaver[fysisk_vagt])

    udsætningsgast_opgaver = [
        Opgave.UDSAETNINGSGAST_A,
        Opgave.UDSAETNINGSGAST_B,
        Opgave.UDSAETNINGSGAST_C,
        Opgave.UDSAETNINGSGAST_D,
        Opgave.UDSAETNINGSGAST_E,
    ]
    for opgave in udsætningsgast_opgaver:
        if opgave not in vagt.opgaver:
            vagt.opgaver[opgave] = pick_least(unavailable_numbers, filter_by_opgave(opgave, skifte_stats))
        unavailable_numbers.append(vagt.opgaver[opgave])

    if time == VagtTid.T15_20:
        # If the last pejlegast b from the skifte is not in the unavailable numbers, create 2 random numbers
        def create_2_pejlegasts() -> None:
            if Opgave.PEJLEGAST_A not in vagt.opgaver:
                vagt.opgaver[Opgave.PEJLEGAST_A] = pick_least(
                    unavailable_numbers, filter_by_opgave(Opgave.PEJLEGAST_A, skifte_stats)
                )
            unavailable_numbers.append(vagt.opgaver[Opgave.PEJLEGAST_A])

            if Opgave.PEJLEGAST_B not in vagt.opgaver:
                vagt.opgaver[Opgave.PEJLEGAST_B] = pick_least(
                    unavailable_numbers, filter_by_opgave(Opgave.PEJLEGAST_B, skifte_stats)
                )
            unavailable_numbers.append(vagt.opgaver[Opgave.PEJLEGAST_B])
        
        # Make the last pejlegast b from the skifte the pejlegast a
        if last_pejlegast_b != -1:
            vagt.opgaver[Opgave.PEJLEGAST_A] = last_pejlegast_b
            unavailable_numbers.append(vagt.opgaver[Opgave.PEJLEGAST_A])

        create_2_pejlegasts()

    if time in [VagtTid.T04_08, VagtTid.T08_12, VagtTid.T12_15, VagtTid.T15_20]:
        if dækselev_i_kabys != 0:
            vagt.opgaver[Opgave.DAEKSELEV_I_KABYS] = dækselev_i_kabys
        elif Opgave.DAEKSELEV_I_KABYS not in vagt.opgaver:
            vagt.opgaver[Opgave.DAEKSELEV_I_KABYS] = pick_least(
                unavailable_numbers, filter_by_opgave(Opgave.DAEKSELEV_I_KABYS, skifte_stats)
            )
        unavailable_numbers.append(vagt.opgaver[Opgave.DAEKSELEV_I_KABYS])

    return vagt


def filter_by_opgave(opgave: Opgave, stats: dict[tuple[Opgave, int], int]) -> dict[tuple[Opgave, int], int]:
    """Filter the stats by opgave"""
    filtered_stats: dict[tuple[Opgave, int], int] = {}

    for (opg, elev_nr), antal in stats.items():
        if opg != opgave:
            continue
        filtered_stats[(opg, elev_nr)] = antal

    return filtered_stats


def filter_by_skifte(skifte: VagtSkifte, stats: dict[tuple[Opgave, int], int]) -> dict[tuple[Opgave, int], int]:
    """Filter the stats by skifte"""
    filtered_stats: dict[tuple[Opgave, int], int] = {}

    for (opg, elev_nr), antal in stats.items():
        if get_skifte_from_elev_nr(elev_nr) != skifte:
            continue
        filtered_stats[(opg, elev_nr)] = antal

    return filtered_stats


def pick_most_days_since(
    unavailable_numbers: list[int], tid: VagtTid, skifte: VagtSkifte, today: date, registry: 'Registry'
) -> int:
    """Pick an available number, which is most days since last picked"""
    # Capture all physical duties, seperated by vagtperiode
    fysiske_vagter: list[tuple[date, tuple[int, VagtTid]]] = []
    for vagtliste in registry.vagtlister:
        for _tid, vagt in vagtliste.vagter.items():
            for opg, nr in vagt.opgaver.items():
                if opg not in [Opgave.UDKIG, Opgave.RADIOVAGT, Opgave.RORGAENGER, Opgave.ORDONNANS]:
                    continue
                fysiske_vagter.append((vagtliste.get_date(), (nr, _tid)))

    # Sample the distances
    fysisk_vagt_days_ago: dict[int, tuple[int, VagtTid]] = {}  # elev_nr is key, days ago is value
    for dato, (elev_nr, _tid) in fysiske_vagter:
        distance = abs((today - dato).days)

        if elev_nr not in fysisk_vagt_days_ago:
            fysisk_vagt_days_ago[elev_nr] = (distance, _tid)

        if fysisk_vagt_days_ago[elev_nr][0] > distance:
            fysisk_vagt_days_ago[elev_nr] = (distance, _tid)

    # Add the missing numbers with infinity days
    for elev_nr in range(63):
        if elev_nr in kabys_elev_nrs:
            continue
        if elev_nr not in fysisk_vagt_days_ago:
            fysisk_vagt_days_ago[elev_nr] = (999999, tid)

    most_days_ago_since_picked_elev_nr = None
    most_days_ago_since_days = -1

    fysisk_vagt_days_ago_list = list(fysisk_vagt_days_ago.items())
    random.shuffle(fysisk_vagt_days_ago_list)
    for elev_nr, (days_ago, _tid) in fysisk_vagt_days_ago_list:
        if get_skifte_from_elev_nr(elev_nr) != skifte:
            continue

        if elev_nr in unavailable_numbers:
            continue

        if is_dagsvagt(_tid) == is_dagsvagt(tid) and days_ago < 10000 and days_ago > 1:
            continue

        if days_ago > most_days_ago_since_days:
            most_days_ago_since_picked_elev_nr = elev_nr
            most_days_ago_since_days = days_ago
    return most_days_ago_since_picked_elev_nr


def pick_least(unavailable_numbers: list[int], stats: dict[tuple[Opgave, int], int]) -> int:
    """Pick the least number"""
    # TODO: There might be a slight bias in this algorithm,
    #       where similar groups are always assigned together
    elev_nr_and_count: list[tuple[int, int]] = []

    for (_, elev_nr), antal in stats.items():
        if elev_nr in unavailable_numbers:
            continue
        elev_nr_and_count.append((elev_nr, antal))

    elev_nr_and_count.sort(key=lambda tup: tup[1])
    if len(elev_nr_and_count) == 0:
        mb.showerror('Error', 'Could not autogenerate vagtliste, no elev_nrs available')
        logging.error(f'Could not find an available number, given these reserved numbers: {unavailable_numbers}')
        logging.error(f'The associated stats: {stats}')
    least_count = elev_nr_and_count[0][1]
    # TODO: Add a random inclusion factor here
    all_least_elev_nr = [elev_nr for elev_nr, count in elev_nr_and_count if count == least_count]
    return random.choice(all_least_elev_nr)


def pick_landgangsvagt(ude_nrs: list[int], skifte: VagtSkifte, vagttid: VagtTid, vls: list[VagtListe]) -> int:
    """Pick the landgangsvagt"""
    vagt_stats: dict[tuple[Opgave, int], int] = {}

    for i in range(1, 64):
        if i in kabys_elev_nrs:
            continue
        vagt_stats[(Opgave.LANDGANGSVAGT_A, i)] = 0

    for vl in vls:
        if vl.vagttype != VagtType.HAVNEVAGT:
            continue

        for tid, vagt in vl.vagter.items():
            if tid != vagttid:
                continue

            for opgave, nr in vagt.opgaver.items():
                if opgave not in [Opgave.LANDGANGSVAGT_A, Opgave.LANDGANGSVAGT_B]:
                    continue

                vagt_stats[(Opgave.LANDGANGSVAGT_A, nr)] += 1

    return pick_least(ude_nrs, filter_by_skifte(skifte, vagt_stats))


def pick_nattevagt(ude_nrs: list[int], skifte: VagtSkifte, vagttid: VagtTid, vls: list[VagtListe]) -> int:
    """Pick the nattevagt"""
    vagt_stats: dict[tuple[Opgave, int], int] = {}

    for i in range(1, 64):
        if i in kabys_elev_nrs:
            continue
        vagt_stats[(Opgave.NATTEVAGT_A, i)] = 0

    for vl in vls:
        if vl.vagttype not in [VagtType.HOLMEN, VagtType.HOLMEN_WEEKEND]:
            continue

        for tid, vagt in vl.vagter.items():
            if tid != vagttid:
                continue

            for opgave, nr in vagt.opgaver.items():
                if opgave not in [Opgave.NATTEVAGT_A, Opgave.NATTEVAGT_B]:
                    continue

                vagt_stats[(Opgave.NATTEVAGT_A, nr)] += 1

    return pick_least(ude_nrs, filter_by_skifte(skifte, vagt_stats))


def count_vagt_stats(all_vls: list[VagtListe]) -> dict[tuple[Opgave, int], int]:
    """Count the vagt stats"""
    vagt_stats: dict[tuple[Opgave, int], int] = {}

    for i in range(1, 64):
        if i in kabys_elev_nrs:
            continue

        for opg in Opgave._member_map_.values():
            vagt_stats[(cast(Any, opg), i)] = 0

    for vagtliste in all_vls:
        for _, vagt_col in vagtliste.vagter.items():
            for opg, elev_nr in vagt_col.opgaver.items():
                merge_opg = Opgave.NATTEVAGT_A if opg == Opgave.NATTEVAGT_B else opg
                vagt_stats[(merge_opg, elev_nr)] += 1

    return vagt_stats


def søvagt_skifte_for_vagttid(begyndende_skifte: VagtSkifte, vagttid: VagtTid) -> VagtSkifte:
    """Get the skifte for the vagttid"""
    skifter: dict[VagtTid, VagtSkifte] = {}

    # Compute the shift for each vagt using modulo
    for index, tid in enumerate(
        [VagtTid.T08_12, VagtTid.T12_15, VagtTid.T15_20, VagtTid.T20_24, VagtTid.T00_04, VagtTid.T04_08]
    ):
        skifter[tid] = VagtSkifte((index + begyndende_skifte.value - 1) % 3 + 1)
    return skifter[vagttid]


def autofill_søvagt_vagtliste(vl: VagtListe, registry: 'Registry', ude_nr: list[int]) -> Optional[str]:
    """Autofill the søvagt vagtliste"""
    vagttider: list[VagtTid] = generate_søvagt_vagttider(vl.start, vl.end)

    for vagttid in vagttider:
        skifte = søvagt_skifte_for_vagttid(vl.starting_shift, vagttid)
        vl.vagter[vagttid] = autofill_vagt(skifte, vagttid, vl, registry, ude_nr)
    return None


def autofill_havnevagt_vagtliste(vl: VagtListe, registry: 'Registry', ude_nr: list[int]) -> Optional[str]:
    """Autofill the havnevagt vagtliste"""
    stats = count_vagt_stats(registry.vagtlister)
    skifte_stats = filter_by_skifte(vl.starting_shift, stats)
    vl.vagter[VagtTid.ALL_DAY] = (
        Vagt(vl.starting_shift, {}) if VagtTid.ALL_DAY not in vl.vagter else vl.vagter[VagtTid.ALL_DAY]
    )

    unavailable_numbers: list[int] = [*ude_nr]

    # Add afmønstringer to unavailable numbers
    for afmønstring in registry.afmønstringer:
        if afmønstring.start_date <= vl.start.date() and afmønstring.end_date >= vl.end.date():
            unavailable_numbers.append(afmønstring.elev_nr)

    # Add ALL_DAY vagter to unavailable numbers
    for _, nr in vl.vagter[VagtTid.ALL_DAY].opgaver.items():
        unavailable_numbers.append(nr)

    # Find HU numbers for the day
    hu_numbers: list[int] = []
    for hu in registry.hu:
        if hu.start_date == vl.start.date():
            hu_numbers.extend(hu.assigned)
            break

    # Pick vagthavende elev
    if Opgave.VAGTHAVENDE_ELEV not in vl.vagter[VagtTid.ALL_DAY].opgaver:
        if vl.chronological_vagthavende:
            vl.vagter[VagtTid.ALL_DAY].opgaver[Opgave.VAGTHAVENDE_ELEV] = get_chronological_vagthavende(
                VagtTid.ALL_DAY, vl, registry, vl.starting_shift, unavailable_numbers
            )
        else:
            last_vagthavende_elev = get_last_vagthavende_from_skifte(
                VagtTid.ALL_DAY,
                vl,
                registry,
                vl.starting_shift,
            )
            vl.vagter[VagtTid.ALL_DAY].opgaver[Opgave.VAGTHAVENDE_ELEV] = pick_least(
                [last_vagthavende_elev, *unavailable_numbers], filter_by_opgave(Opgave.VAGTHAVENDE_ELEV, skifte_stats)
            )
    unavailable_numbers.append(vl.vagter[VagtTid.ALL_DAY].opgaver[Opgave.VAGTHAVENDE_ELEV])

    # Pick dækselev
    if Opgave.DAEKSELEV_I_KABYS not in vl.vagter[VagtTid.ALL_DAY].opgaver:
        vl.vagter[VagtTid.ALL_DAY].opgaver[Opgave.DAEKSELEV_I_KABYS] = pick_least(
            [*hu_numbers, *unavailable_numbers], filter_by_opgave(Opgave.DAEKSELEV_I_KABYS, skifte_stats)
        )
    unavailable_numbers.append(vl.vagter[VagtTid.ALL_DAY].opgaver[Opgave.DAEKSELEV_I_KABYS])

    # Flag to determine if the vagter are being solved from scratch
    scratch_solve = True

    # Pick landgangsvagter
    havne_vagt_tider = generate_havnevagt_vagttider(vl.start, vl.end)

    # Split the landgangsvagter into two groups, dagsvagter and nattevagter
    dagsvagter, nattevagter = separate_havnevagt_dagsvagter_nattevagter(havne_vagt_tider)

    assigned_dagsvagter: list[int] = []
    assigned_nattevagter: list[int] = []
    last_two_assignments: collections.deque[int] = collections.deque(maxlen=4)

    for tid in dagsvagter:
        vl.vagter[tid] = Vagt(vl.starting_shift, {}) if tid not in vl.vagter else vl.vagter[tid]

        if scratch_solve and vl.vagter[tid].opgaver != {}:
            scratch_solve = False

        excluded_hu_numbers = []
        if tid in [VagtTid.T08_12, VagtTid.T12_16]:
            excluded_hu_numbers = hu_numbers

        if Opgave.LANDGANGSVAGT_A not in vl.vagter[tid].opgaver:
            vl.vagter[tid].opgaver[Opgave.LANDGANGSVAGT_A] = pick_landgangsvagt(
                [*unavailable_numbers, *assigned_dagsvagter, *excluded_hu_numbers],
                vl.starting_shift,
                tid,
                registry.vagtlister,
            )

        assigned_dagsvagter.append(vl.vagter[tid].opgaver[Opgave.LANDGANGSVAGT_A])
        last_two_assignments.append(vl.vagter[tid].opgaver[Opgave.LANDGANGSVAGT_A])

        if Opgave.LANDGANGSVAGT_B not in vl.vagter[tid].opgaver:
            vl.vagter[tid].opgaver[Opgave.LANDGANGSVAGT_B] = pick_landgangsvagt(
                [*unavailable_numbers, *assigned_dagsvagter, *excluded_hu_numbers],
                vl.starting_shift,
                tid,
                registry.vagtlister,
            )

        assigned_dagsvagter.append(vl.vagter[tid].opgaver[Opgave.LANDGANGSVAGT_B])
        last_two_assignments.append(vl.vagter[tid].opgaver[Opgave.LANDGANGSVAGT_B])

    # Remove vagthavende elev from unavailable numbers
    unavailable_numbers.remove(vl.vagter[VagtTid.ALL_DAY].opgaver[Opgave.VAGTHAVENDE_ELEV])

    for tid in nattevagter:
        vl.vagter[tid] = Vagt(vl.starting_shift, {}) if tid not in vl.vagter else vl.vagter[tid]

        if scratch_solve and vl.vagter[tid].opgaver != {}:
            scratch_solve = False

        if Opgave.LANDGANGSVAGT_A not in vl.vagter[tid].opgaver:
            vl.vagter[tid].opgaver[Opgave.LANDGANGSVAGT_A] = pick_landgangsvagt(
                [*unavailable_numbers, *assigned_nattevagter, *last_two_assignments],
                vl.starting_shift,
                tid,
                registry.vagtlister,
            )

        assigned_nattevagter.append(vl.vagter[tid].opgaver[Opgave.LANDGANGSVAGT_A])
        last_two_assignments.append(vl.vagter[tid].opgaver[Opgave.LANDGANGSVAGT_A])

        if Opgave.LANDGANGSVAGT_B not in vl.vagter[tid].opgaver:
            vl.vagter[tid].opgaver[Opgave.LANDGANGSVAGT_B] = pick_landgangsvagt(
                [*unavailable_numbers, *assigned_nattevagter, *last_two_assignments],
                vl.starting_shift,
                tid,
                registry.vagtlister,
            )

        assigned_nattevagter.append(vl.vagter[tid].opgaver[Opgave.LANDGANGSVAGT_B])
        last_two_assignments.append(vl.vagter[tid].opgaver[Opgave.LANDGANGSVAGT_B])

    if scratch_solve:
        time_53, opg_53 = None, None

        for tid, vagt in vl.vagter.items():
            if is_dagsvagt(tid):
                continue

            if Opgave.LANDGANGSVAGT_A in vagt.opgaver and vagt.opgaver[Opgave.LANDGANGSVAGT_A] == 53:
                time_53, opg_53 = tid, Opgave.LANDGANGSVAGT_A
                break
            if Opgave.LANDGANGSVAGT_B in vagt.opgaver and vagt.opgaver[Opgave.LANDGANGSVAGT_B] == 53:
                time_53, opg_53 = tid, Opgave.LANDGANGSVAGT_B
                break

        if time_53 is not None and time_53 != VagtTid.T04_06 and opg_53 is not None and VagtTid.T04_06 in vl.vagter:
            vagt_type = random.choice([Opgave.LANDGANGSVAGT_A, Opgave.LANDGANGSVAGT_B])
            vl.vagter[time_53].opgaver[opg_53], vl.vagter[VagtTid.T04_06].opgaver[vagt_type] = (
                vl.vagter[VagtTid.T04_06].opgaver[vagt_type],
                vl.vagter[time_53].opgaver[opg_53],
            )

    return None


def autofill_holmen_vagtliste(vl: VagtListe, registry: 'Registry', ude_nr: list[int]) -> Optional[str]:
    """Autofill the holmen vagtliste"""
    stats = count_vagt_stats(registry.vagtlister)
    skifte_stats = filter_by_skifte(vl.starting_shift, stats)
    vl.vagter[VagtTid.ALL_DAY] = (
        Vagt(vl.starting_shift, {}) if VagtTid.ALL_DAY not in vl.vagter else vl.vagter[VagtTid.ALL_DAY]
    )

    unavailable_numbers: list[int] = [*ude_nr]

    # Add afmønstringer to unavailable numbers
    for afmønstring in registry.afmønstringer:
        if afmønstring.start_date <= vl.start.date() and afmønstring.end_date >= vl.end.date():
            unavailable_numbers.append(afmønstring.elev_nr)

    # Add ALL_DAY vagter to unavailable numbers
    for _, nr in vl.vagter[VagtTid.ALL_DAY].opgaver.items():
        unavailable_numbers.append(nr)

    # Pick vagthavende elev
    if Opgave.VAGTHAVENDE_ELEV not in vl.vagter[VagtTid.ALL_DAY].opgaver:
        if vl.chronological_vagthavende:
            vl.vagter[VagtTid.ALL_DAY].opgaver[Opgave.VAGTHAVENDE_ELEV] = get_chronological_vagthavende(
                VagtTid.ALL_DAY, vl, registry, vl.starting_shift, unavailable_numbers
            )
        else:
            last_vagthavende_elev = get_last_vagthavende_from_skifte(
                VagtTid.ALL_DAY,
                vl,
                registry,
                vl.starting_shift,
            )

            vl.vagter[VagtTid.ALL_DAY].opgaver[Opgave.VAGTHAVENDE_ELEV] = pick_least(
                [last_vagthavende_elev, *unavailable_numbers], filter_by_opgave(Opgave.VAGTHAVENDE_ELEV, skifte_stats)
            )
    unavailable_numbers.append(vl.vagter[VagtTid.ALL_DAY].opgaver[Opgave.VAGTHAVENDE_ELEV])

    # Pick dækselev
    if vl.holmen_dækselev_i_kabys:
        if Opgave.DAEKSELEV_I_KABYS not in vl.vagter[VagtTid.ALL_DAY].opgaver:
            vl.vagter[VagtTid.ALL_DAY].opgaver[Opgave.DAEKSELEV_I_KABYS] = pick_least(
                unavailable_numbers, filter_by_opgave(Opgave.DAEKSELEV_I_KABYS, skifte_stats)
            )
        unavailable_numbers.append(vl.vagter[VagtTid.ALL_DAY].opgaver[Opgave.DAEKSELEV_I_KABYS])

    # Pick nattevagter
    holmen_vagt_tider = generate_holmen_vagttider(vl.start, vl.end)
    scratch_solve = True
    assigned_nattevagter: list[int] = []
    for tid in holmen_vagt_tider:
        if tid == VagtTid.ALL_DAY:
            continue

        vl.vagter[tid] = Vagt(vl.starting_shift, {}) if tid not in vl.vagter else vl.vagter[tid]
        if scratch_solve and vl.vagter[tid].opgaver != {}:
            scratch_solve = False

        if Opgave.NATTEVAGT_A not in vl.vagter[tid].opgaver:
            vl.vagter[tid].opgaver[Opgave.NATTEVAGT_A] = pick_nattevagt(
                [*unavailable_numbers, *assigned_nattevagter],
                vl.starting_shift,
                tid,
                registry.vagtlister,
            )

            assigned_nattevagter.append(vl.vagter[tid].opgaver[Opgave.NATTEVAGT_A])

        if vl.holmen_double_nattevagt:
            if Opgave.NATTEVAGT_B not in vl.vagter[tid].opgaver:
                vl.vagter[tid].opgaver[Opgave.NATTEVAGT_B] = pick_nattevagt(
                    [*unavailable_numbers, *assigned_nattevagter],
                    vl.starting_shift,
                    tid,
                    registry.vagtlister,
                )
                assigned_nattevagter.append(vl.vagter[tid].opgaver[Opgave.NATTEVAGT_B])

    if scratch_solve:
        time_53, opg_53 = None, None

        for tid, vagt in vl.vagter.items():
            if Opgave.NATTEVAGT_A in vagt.opgaver and vagt.opgaver[Opgave.NATTEVAGT_A] == 53:
                time_53, opg_53 = tid, Opgave.NATTEVAGT_A
                break
            if Opgave.NATTEVAGT_B in vagt.opgaver and vagt.opgaver[Opgave.NATTEVAGT_B] == 53:
                time_53, opg_53 = tid, Opgave.NATTEVAGT_B
                break

        if time_53 is not None and time_53 != VagtTid.T04_06 and opg_53 is not None and VagtTid.T04_06 in vl.vagter:
            vagt_type = (
                random.choice([Opgave.NATTEVAGT_A, Opgave.NATTEVAGT_B])
                if vl.holmen_double_nattevagt
                else Opgave.NATTEVAGT_A
            )
            vl.vagter[time_53].opgaver[opg_53], vl.vagter[VagtTid.T04_06].opgaver[vagt_type] = (
                vl.vagter[VagtTid.T04_06].opgaver[vagt_type],
                vl.vagter[time_53].opgaver[opg_53],
            )

    return None


def autofill_vagtliste(vl: VagtListe, registry: 'Registry', ude_nr: Optional[list[int]] = None) -> Optional[str]:
    """Autofill the vagtliste"""
    if ude_nr is None:
        ude_nr = []

    if vl.vagttype == VagtType.SOEVAGT:
        return autofill_søvagt_vagtliste(vl, registry, ude_nr)
    if vl.vagttype == VagtType.HAVNEVAGT:
        return autofill_havnevagt_vagtliste(vl, registry, ude_nr)
    if vl.vagttype in [VagtType.HOLMEN, VagtType.HOLMEN_WEEKEND]:
        return autofill_holmen_vagtliste(vl, registry, ude_nr)
    return 'Unknown vagttype'
