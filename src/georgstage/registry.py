"""This module contains the registry, responsible for loading and storing data"""

from datetime import datetime

from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from georgstage.model import VagtListe, VagtPeriode, VagtSkifte, VagtType
from georgstage.solver import autofill_vagtliste
from uuid import UUID, uuid4

class Registry(BaseModel):
    """The registry is responsible for loading and storing data"""

    vagtperioder: list[VagtPeriode] = []
    vagtlister: list[VagtListe] = []
    event_listeners: list = Field([], exclude=True)

    def get_vagtperiode_by_id(self, id: UUID) -> VagtPeriode:
        for vp in self.vagtperioder:
            if vp.id == id:
                return vp
        raise ValueError(f'No VagtPeriode with id: {id}')

    def add_vagtperiode(self, vagtperiode: VagtPeriode) -> None:
        """Add a vagtperiode to the registry"""
        self.vagtperioder.append(vagtperiode)
        new_vl_stubs = vagtperiode.get_vagtliste_stubs()
        for new_vl in new_vl_stubs:
            error = autofill_vagtliste(new_vl, self.vagtlister)
            if error is not None:
                print(error)
            self.vagtlister.append(new_vl)
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
                if vl.vagttype == new_vl.vagttype and vl.start.date() == new_vl.start.date() and vl.end.date() == new_vl.end.date():
                    vl_should_be_kept = True
                    break
            if not vl_should_be_kept:
                self.vagtlister.remove(vl)
        
        # Add any new vagtlister that are produced by the vagtperiode
        for new_vl in new_vl_stubs:
            vl_already_exists = False
            for vl in self.vagtlister:
                if vl.vagttype == new_vl.vagttype and vl.start.date() == new_vl.start.date() and vl.end.date() == new_vl.end.date():
                    vl_already_exists = True
                    break
            if vl_already_exists:
                continue
            error = autofill_vagtliste(new_vl, self.vagtlister)
            if error is not None:
                print(error)
            self.vagtlister.append(new_vl)
        
        self.notify_update_listeners()
        

    def remove_vagtperiode(self, vagtperiode: VagtPeriode) -> None:
        """Remove a vagtperiode from the registry"""
        self.vagtperioder.remove(vagtperiode)

        # Remove all vagtlister that were produced by the vagtperiode
        for vl in self.vagtlister:
            if vl.vagtperiode_id == vagtperiode.id:
                self.vagtlister.remove(vl)

        self.notify_update_listeners()



    def register_update_listener(self, listener) -> None:
        self.event_listeners.append(listener)

    def notify_update_listeners(self) -> None:
        for listener in self.event_listeners:
            listener()


if __name__ == '__main__':
    registry = Registry()
    registry.add_vagtperiode(
        VagtPeriode(
            uuid4(),
            VagtType.SOEVAGT,
            datetime.fromisoformat('2024-12-02 13:00'),
            datetime.fromisoformat('2024-12-06 14:00'),
            'Korsør-Helsinki',
            VagtSkifte.SKIFTE_2,
        )
    )

    # registry.add_vagtperiode(
    #     VagtPeriode(
    #         VagtType.HAVNEVAGT,
    #         datetime.fromisoformat('2024-12-06 14:00'),
    #         datetime.fromisoformat('2024-12-12 18:00'),
    #         'Helsinki',
    #         VagtSkifte.SKIFTE_3,
    #     )
    # )