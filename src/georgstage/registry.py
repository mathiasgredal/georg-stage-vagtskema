"""This module contains the registry, responsible for loading and storing data"""

import collections
import json
import logging
import pathlib
from typing import Callable, Optional
from uuid import UUID

from georgstage.model import HU, Afmønstring, VagtListe, VagtPeriode
from georgstage.solver import autofill_vagtliste
from georgstage.util import EnhancedJSONDecoder, EnhancedJSONEncoder


class Registry:
    """The registry is responsible for loading and storing data"""

    vagtperioder: list[VagtPeriode] = []
    vagtlister: list[VagtListe] = []
    afmønstringer: list[Afmønstring] = []
    hu: list[HU] = []
    event_listeners: list[Callable[[], None]] = []
    versions: collections.deque[str] = collections.deque(maxlen=50)
    redo_stack: collections.deque[str] = collections.deque(maxlen=50)

    def load_from_string(self, data_str: str) -> None:
        """Load the registry from a string"""
        data = json.loads(data_str, cls=EnhancedJSONDecoder)
        self.vagtperioder = [VagtPeriode(**vp) for vp in data['vagtperioder']]
        self.vagtlister = [VagtListe(**vl) for vl in data['vagtlister']]
        self.afmønstringer = [Afmønstring(**af) for af in data['afmønstringer']]
        self.hu = [HU(**h) for h in data['hu']] if 'hu' in data else []
        self.notify_update_listeners(pure_update=True)

    def load_from_file(self, filename: pathlib.Path) -> None:
        """Load the registry from a file"""
        self.load_from_string(pathlib.Path(filename).read_text())

    def save_to_string(self) -> str:
        """Save the registry to a string"""
        data = {
            'vagtperioder': self.vagtperioder,
            'vagtlister': self.vagtlister,
            'afmønstringer': self.afmønstringer,
            'hu': self.hu,
        }
        return json.dumps(data, cls=EnhancedJSONEncoder, ensure_ascii=False, indent=4)

    def save_to_file(self, filename: pathlib.Path) -> None:
        """Save the registry to a file"""
        pathlib.Path(filename).write_text(self.save_to_string())

    def get_vagtperiode_by_id(self, id: UUID) -> Optional[VagtPeriode]:
        """Get a vagtperiode by id"""
        for vp in self.vagtperioder:
            if vp.id == id:
                return vp
        return None

    def add_vagtperiode(self, vagtperiode: VagtPeriode) -> None:
        """Add a vagtperiode to the registry"""
        self.vagtperioder.append(vagtperiode)
        new_vl_stubs = vagtperiode.get_vagtliste_stubs()
        for new_vl in new_vl_stubs:
            error = autofill_vagtliste(new_vl, self)
            if error is not None:
                logging.error(error)
            self.vagtlister.append(new_vl)
        self.vagtlister.sort(key=lambda vl: vl.start)
        self.notify_update_listeners()

    def update_vagtperiode(self, id: UUID, vagtperiode: VagtPeriode, notify: bool = True) -> None:
        """Update a vagtperiode in the registry"""
        # When we update a vagtperiode, we need to find all the vagtlister that were produced by it
        # and update them as well
        for vp in self.vagtperioder:
            if vp.id == id:
                vp.vagttype = vagtperiode.vagttype
                vp.start = vagtperiode.start
                vp.end = vagtperiode.end
                vp.note = vagtperiode.note
                vp.starting_shift = vagtperiode.starting_shift
                vp.holmen_double_nattevagt = vagtperiode.holmen_double_nattevagt
                vp.holmen_dækselev_i_kabys = vagtperiode.holmen_dækselev_i_kabys
                vp.chronological_vagthavende = vagtperiode.chronological_vagthavende
                vp.initial_vagthavende_first_shift = vagtperiode.initial_vagthavende_first_shift
                vp.initial_vagthavende_second_shift = vagtperiode.initial_vagthavende_second_shift
                vp.initial_vagthavende_third_shift = vagtperiode.initial_vagthavende_third_shift
                break

        new_vl_stubs = vagtperiode.get_vagtliste_stubs()
        existing_vl_stubs = [vl for vl in self.vagtlister if vl.vagtperiode_id == id]

        # Remove any vagtlister that are no longer produced by the vagtperiode
        for vl in existing_vl_stubs:
            vl_should_be_kept = False
            for new_vl in new_vl_stubs:
                if (
                    vl.vagttype == new_vl.vagttype
                    and vl.starting_shift == new_vl.starting_shift
                    and vl.start == new_vl.start
                    and vl.end == new_vl.end
                    and vl.holmen_double_nattevagt == new_vl.holmen_double_nattevagt
                    and vl.holmen_dækselev_i_kabys == new_vl.holmen_dækselev_i_kabys
                    and vl.chronological_vagthavende == new_vl.chronological_vagthavende
                    and vl.initial_vagthavende_first_shift == new_vl.initial_vagthavende_first_shift
                    and vl.initial_vagthavende_second_shift == new_vl.initial_vagthavende_second_shift
                    and vl.initial_vagthavende_third_shift == new_vl.initial_vagthavende_third_shift
                ):
                    vl_should_be_kept = True
                    break
            if not vl_should_be_kept:
                self.vagtlister.remove(vl)

        # Add any new vagtlister that are produced by the vagtperiode
        for new_vl in new_vl_stubs:
            vl_already_exists = False
            for vl in self.vagtlister:
                if vl.vagttype == new_vl.vagttype and vl.start == new_vl.start and vl.end == new_vl.end:
                    vl_already_exists = True
                    break
            if vl_already_exists:
                continue
            error = autofill_vagtliste(new_vl, self)
            if error is not None:
                logging.error(error)
            self.vagtlister.append(new_vl)
        self.vagtlister.sort(key=lambda vl: vl.start)

        if notify:
            self.notify_update_listeners()

    def remove_vagtperiode(self, vagtperiode: VagtPeriode) -> None:
        """Remove a vagtperiode from the registry"""
        self.vagtperioder.remove(vagtperiode)
        self.vagtlister = [vl for vl in self.vagtlister if vl.vagtperiode_id != vagtperiode.id]

        self.notify_update_listeners()

    def get_afmønstring_by_id(self, id: UUID) -> Optional[Afmønstring]:
        """Get an afmønstring by id"""
        for afmønstring in self.afmønstringer:
            if afmønstring.id == id:
                return afmønstring
        return None

    def register_update_listener(self, listener: Callable[[], None]) -> None:
        """Register an update listener"""
        self.event_listeners.append(listener)

    def undo_last_update(self) -> None:
        """Undo the last update"""
        if len(self.versions) <= 1:
            return
        self.redo_stack.append(self.versions.pop())
        self.load_from_string(self.versions[-1])

    def redo_last_update(self) -> None:
        """Redo the last update"""
        if len(self.redo_stack) == 0:
            return
        last_version = self.redo_stack.pop()
        self.versions.append(last_version)
        self.load_from_string(last_version)

    def notify_update_listeners(self, pure_update: bool = False) -> None:
        """Notify update listeners"""
        version = self.save_to_string()
        if not pure_update and len(self.versions) == 0 or len(self.versions) > 0 and version != self.versions[-1]:
            self.versions.append(version)
            self.redo_stack.clear()

        for listener in self.event_listeners:
            listener()
