"""This module contains the registry, responsible for loading and storing data"""

from georgstage.model import VagtListe, VagtPeriode, Afmønstring
from georgstage.solver import autofill_vagtliste
from uuid import UUID
from georgstage.util import EnhancedJSONDecoder, EnhancedJSONEncoder
import json
import pathlib


class Registry:
    """The registry is responsible for loading and storing data"""

    vagtperioder: list[VagtPeriode] = []
    vagtlister: list[VagtListe] = []
    afmønstringer: list[Afmønstring] = []
    event_listeners: list[callable] = []

    def load_from_file(self, filename: str) -> None:
        """Load the registry from a file"""
        data = json.loads(pathlib.Path(filename).read_text(), cls=EnhancedJSONDecoder)
        self.vagtperioder = [VagtPeriode(**vp) for vp in data['vagtperioder']]
        self.vagtlister = [VagtListe(**vl) for vl in data['vagtlister']]
        self.afmønstringer = [Afmønstring(**af) for af in data['afmønstringer']]
        self.notify_update_listeners()

    def save_to_string(self) -> str:
        data = {
            'vagtperioder': self.vagtperioder,
            'vagtlister': self.vagtlister,
            'afmønstringer': self.afmønstringer,
        }
        return json.dumps(data, cls=EnhancedJSONEncoder, ensure_ascii=False, indent=4)

    def save_to_file(self, filename: str) -> None:
        """Save the registry to a file"""
        pathlib.Path(filename).write_text(self.save_to_string())

    def get_vagtperiode_by_id(self, id: UUID) -> VagtPeriode | None:
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
                print(error)
            self.vagtlister.append(new_vl)
        self.vagtlister.sort(key=lambda vl: vl.start)
        self.notify_update_listeners()

    def update_vagtperiode(self, id: UUID, vagtperiode: VagtPeriode) -> None:
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
                print(error)
            self.vagtlister.append(new_vl)
        self.vagtlister.sort(key=lambda vl: vl.start)
        self.notify_update_listeners()

    def remove_vagtperiode(self, vagtperiode: VagtPeriode) -> None:
        """Remove a vagtperiode from the registry"""
        self.vagtperioder.remove(vagtperiode)
        self.vagtlister = [vl for vl in self.vagtlister if vl.vagtperiode_id != vagtperiode.id]

        self.notify_update_listeners()

    def get_afmønstring_by_id(self, id: UUID) -> Afmønstring | None:
        for afmønstring in self.afmønstringer:
            if afmønstring.id == id:
                return afmønstring
        return None

    def register_update_listener(self, listener) -> None:
        self.event_listeners.append(listener)

    def notify_update_listeners(self) -> None:
        for listener in self.event_listeners:
            listener()
