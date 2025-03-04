"""Tab for managing vagtperioder"""

import tkinter as tk
from datetime import datetime, timedelta
from tkinter import ttk
from typing import Any, Optional
from uuid import UUID, uuid4

from georgstage.model import VagtPeriode, VagtSkifte, VagtType
from georgstage.registry import Registry
from georgstage.util import make_cell


class VagtPeriodeTab(ttk.Frame):
    """Tab for managing vagtperioder"""

    def __init__(self, parent: tk.Misc, registry: Registry) -> None:
        ttk.Frame.__init__(self, parent, padding=(5, 5, 12, 5))
        self.registry = registry

        # State variables
        self.vagtperiode_type = tk.StringVar()
        self.vagtperiode_type.trace_add('write', self.on_set_vagtperiode_type)
        self.selected_shift = tk.StringVar()
        self.vagtperioder_var = tk.Variable()
        self.note_var = tk.StringVar()
        self.chronological_vagthavende_var = tk.IntVar(value=0)
        self.chronological_vagthavende_var.trace_add('write', self.on_check_chronological_vagthavende)
        self.initial_vagthavende_first_shift_var = tk.IntVar(value=0)
        self.initial_vagthavende_second_shift_var = tk.IntVar(value=0)
        self.initial_vagthavende_third_shift_var = tk.IntVar(value=0)
        self.holmen_double_nattevagt_var = tk.IntVar(value=0)
        self.holmen_dækselev_i_kabys_var = tk.IntVar(value=0)

        self.vagtperioder_listbox = tk.Listbox(
            self, listvariable=self.vagtperioder_var, height=15, selectmode=tk.SINGLE, exportselection=False
        )
        self.vagtperioder_listbox.bind('<<ListboxSelect>>', self.on_select_period)

        # Vagtperiode Form
        self.vagtperiode_frame = ttk.Frame(self)
        self.type_label = ttk.Label(self.vagtperiode_frame, text='Type af vagtperiode:')
        self.type_opt1 = ttk.Radiobutton(
            self.vagtperiode_frame, text='Søvagt', variable=self.vagtperiode_type, value=VagtType.SOEVAGT.value
        )
        self.type_opt2 = ttk.Radiobutton(
            self.vagtperiode_frame, text='Havnevagt', variable=self.vagtperiode_type, value=VagtType.HAVNEVAGT.value
        )
        self.type_opt3 = ttk.Radiobutton(
            self.vagtperiode_frame, text='Holmen', variable=self.vagtperiode_type, value=VagtType.HOLMEN.value
        )
        self.type_opt4 = ttk.Radiobutton(
            self.vagtperiode_frame, text='Weekend', variable=self.vagtperiode_type, value=VagtType.HOLMEN_WEEKEND.value
        )

        self.startdate_label = ttk.Label(self.vagtperiode_frame, text='Start:')
        self.startdate_var = tk.StringVar()
        self.startdate_entry = ttk.Entry(self.vagtperiode_frame, textvariable=self.startdate_var)

        self.enddate_label = ttk.Label(self.vagtperiode_frame, text='Slut:')
        self.enddate_var = tk.StringVar()
        self.enddate_entry = ttk.Entry(self.vagtperiode_frame, textvariable=self.enddate_var)

        self.vagtskifte_label = ttk.Label(self.vagtperiode_frame, text='Begyndende skifte:')
        self.vagtskifte_opts = {' 1#': VagtSkifte.SKIFTE_1, ' 2#': VagtSkifte.SKIFTE_2, ' 3#': VagtSkifte.SKIFTE_3}
        self.vagtskifte_entry = ttk.OptionMenu(
            self.vagtperiode_frame,
            self.selected_shift,
            list(self.vagtskifte_opts.keys())[0],
            *self.vagtskifte_opts.keys(),
        )

        self.note_label = ttk.Label(self.vagtperiode_frame, text='Note:')
        self.note_entry = ttk.Entry(self.vagtperiode_frame, textvariable=self.note_var)

        self.holmen_double_nattevagt_label = ttk.Checkbutton(
            self.vagtperiode_frame,
            text='Holmen: Dobbelt nattevagt',
            variable=self.holmen_double_nattevagt_var,
        )

        self.holmen_dækselev_i_kabys_label = ttk.Checkbutton(
            self.vagtperiode_frame,
            text='Holmen: Dækselev i kabys',
            variable=self.holmen_dækselev_i_kabys_var,
        )

        self.vagthavende_label = ttk.Checkbutton(
            self.vagtperiode_frame,
            text='Kronologisk vagthavende ELEV:',
            variable=self.chronological_vagthavende_var,
        )
        self.vagthavende_entry_frame = tk.Frame(self.vagtperiode_frame)

        make_cell(self.vagthavende_entry_frame, 0, 0, '1#', 6, True, ipadx=2)
        make_cell(self.vagthavende_entry_frame, 0, 1, '2#', 6, True, ipadx=1)
        make_cell(self.vagthavende_entry_frame, 0, 2, '3#', 6, True, ipadx=2)
        make_cell(self.vagthavende_entry_frame, 1, 0, '', 6, False, self.initial_vagthavende_first_shift_var, ipadx=2)
        make_cell(self.vagthavende_entry_frame, 1, 1, '', 6, False, self.initial_vagthavende_second_shift_var, ipadx=1)
        make_cell(self.vagthavende_entry_frame, 1, 2, '', 6, False, self.initial_vagthavende_third_shift_var, ipadx=2)

        self.add_remove_frame = ttk.Frame(self)
        self.add = ttk.Button(self.add_remove_frame, text='Tilføj...', command=self.add_item)
        self.remove = ttk.Button(self.add_remove_frame, text='Fjern', command=self.remove_item)
        self.send_btn = ttk.Button(self, text='Anvend', default='active', command=self.save_action)

        # Grid all the widgets
        self.vagtperioder_listbox.grid(
            column=0,
            row=0,
            sticky='nsew',
        )

        self.vagtperiode_frame.grid(column=1, row=0, sticky='wn')

        self.type_label.grid(column=0, row=0, sticky='w', padx=10, pady=5)
        self.type_opt1.grid(column=0, row=1, sticky='w', padx=20)
        self.type_opt2.grid(column=0, row=2, sticky='w', padx=20)
        self.type_opt3.grid(column=0, row=4, sticky='w', padx=20)
        self.type_opt4.grid(column=0, row=5, sticky='w', padx=20)

        self.startdate_label.grid(column=0, row=6, sticky='w', padx=10, pady=(5, 0))
        self.startdate_entry.grid(column=0, row=7, sticky='w', padx=20)

        self.enddate_label.grid(column=0, row=8, sticky='w', padx=10, pady=(5, 0))
        self.enddate_entry.grid(column=0, row=9, sticky='w', padx=20)

        self.vagtskifte_label.grid(column=0, row=10, sticky='w', padx=10, pady=(5, 0))
        self.vagtskifte_entry.grid(column=0, row=11, sticky='w', padx=20, pady=2.5)

        self.note_label.grid(column=0, row=12, sticky='w', padx=10, pady=(5, 0))
        self.note_entry.grid(column=0, row=13, sticky='w', padx=20)

        self.vagthavende_label.grid(column=0, row=16, sticky='w', padx=10, pady=(5, 0))
        self.vagthavende_entry_frame.grid(column=0, row=17, sticky='w', padx=20)

        self.send_btn.grid(column=1, row=1, sticky=tk.E)
        self.add_remove_frame.grid(column=0, row=1, pady=(5, 0), sticky='we')

        self.add.grid(column=0, row=1, sticky=(tk.W), pady=(0, 5))
        self.remove.grid(column=1, row=1, sticky=(tk.W), padx=10, pady=(0, 5))

        # Make the listbox column expand
        self.grid_columnconfigure(0, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # Select the first item
        self.selected_vp_id: Optional[UUID] = (
            self.registry.vagtperioder[0].id if len(self.registry.vagtperioder) > 0 else None
        )
        self.sync_form()
        self.sync_list()

        # Register event listeners
        self.registry.register_update_listener(self.on_update_registry)

    def on_select_period(self, event: tk.Event) -> None:  # type: ignore
        """Select the period and sync the form"""
        w = event.widget
        if len(w.curselection()) == 0:
            return
        index = int(w.curselection()[0])
        self.selected_vp_id = self.registry.vagtperioder[index].id
        self.sync_form()

    def on_set_vagtperiode_type(self, *args: Any) -> None:
        """Set the vagtperiode type and sync the form"""
        if self.vagtperiode_type.get() in [VagtType.HOLMEN.value, VagtType.HOLMEN_WEEKEND.value]:
            self.holmen_double_nattevagt_label.grid(column=0, row=14, sticky='w', padx=10, pady=(5, 0))
            self.holmen_dækselev_i_kabys_label.grid(column=0, row=15, sticky='w', padx=10, pady=(5, 0))
        else:
            self.holmen_double_nattevagt_label.grid_remove()
            self.holmen_dækselev_i_kabys_label.grid_remove()

    def on_check_chronological_vagthavende(self, *args: Any) -> None:
        """Check if the vagthavende is chronological and sync the form"""
        if self.chronological_vagthavende_var.get() == 0:
            self.vagthavende_entry_frame.grid_forget()
        else:
            self.vagthavende_entry_frame.grid()

    def sync_list(self) -> None:
        """Sync the list with the registry"""
        self.vagtperioder_var.set([vagtperiode.to_string() for vagtperiode in self.registry.vagtperioder])
        self.vagtperioder_listbox.select_clear(0, tk.END)
        selected_index = self._get_vp_index(self.selected_vp_id)
        if selected_index is not None:
            self.vagtperioder_listbox.selection_set(selected_index)
        for i in range(0, len(self.vagtperioder_var.get()), 2):  # type: ignore
            self.vagtperioder_listbox.itemconfigure(i, background='#f0f0ff')

    def sync_form(self) -> None:
        """Sync the form with the selected item"""
        if len(self.registry.vagtperioder) == 0:
            return

        if self.selected_vp_id is None:
            self.selected_vp_id = self.registry.vagtperioder[0].id

        selected_vagtperiode = self.registry.get_vagtperiode_by_id(self.selected_vp_id)
        if selected_vagtperiode is None:
            self.selected_vp_id = self.registry.vagtperioder[0].id
            selected_vagtperiode = self.registry.vagtperioder[0]
        self.startdate_var.set(selected_vagtperiode.start.strftime('%Y-%m-%d %H:%M'))
        self.enddate_var.set(selected_vagtperiode.end.strftime('%Y-%m-%d %H:%M'))
        for key, value in self.vagtskifte_opts.items():
            if value == selected_vagtperiode.starting_shift:
                self.selected_shift.set(key)
                break
        self.vagtperiode_type.set(selected_vagtperiode.vagttype.value)
        self.note_var.set(selected_vagtperiode.note)
        self.holmen_double_nattevagt_var.set(selected_vagtperiode.holmen_double_nattevagt)
        self.holmen_dækselev_i_kabys_var.set(selected_vagtperiode.holmen_dækselev_i_kabys)
        self.chronological_vagthavende_var.set(selected_vagtperiode.chronological_vagthavende)
        self.initial_vagthavende_first_shift_var.set(selected_vagtperiode.initial_vagthavende_first_shift)
        self.initial_vagthavende_second_shift_var.set(selected_vagtperiode.initial_vagthavende_second_shift)
        self.initial_vagthavende_third_shift_var.set(selected_vagtperiode.initial_vagthavende_third_shift)

    def save_action(self) -> None:
        """Save the current item and sync the list and form"""
        if len(self.registry.vagtperioder) == 0:
            return

        if self.startdate_var.get() > self.enddate_var.get():
            raise ValueError('Start dato skal være før slut dato')

        if self.selected_vp_id is None:
            raise ValueError('Ingen vagtperiode valgt')

        new_vagtperiode = VagtPeriode(
            self.selected_vp_id,
            VagtType(self.vagtperiode_type.get()),
            datetime.fromisoformat(self.startdate_var.get()),
            datetime.fromisoformat(self.enddate_var.get()),
            self.note_var.get(),
            self.vagtskifte_opts[self.selected_shift.get()],
            self.holmen_double_nattevagt_var.get() == 1,
            self.holmen_dækselev_i_kabys_var.get() == 1,
            self.chronological_vagthavende_var.get() == 1,
            self.initial_vagthavende_first_shift_var.get(),
            self.initial_vagthavende_second_shift_var.get(),
            self.initial_vagthavende_third_shift_var.get(),
        )

        self.registry.update_vagtperiode(self.selected_vp_id, new_vagtperiode)
        self.sync_list()

    def add_item(self) -> None:
        """Add a new item to the registry and sync the list and form"""
        last_vp = self.registry.vagtperioder[-1] if len(self.registry.vagtperioder) > 0 else None
        next_start_date = last_vp.end if last_vp is not None else datetime.now().replace(minute=0)
        next_end_date = next_start_date + timedelta(days=2)
        self.registry.add_vagtperiode(
            VagtPeriode(
                id=uuid4(),
                vagttype=VagtType.SOEVAGT,
                start=next_start_date,
                end=next_end_date,
                note='FRA-TIL',
                starting_shift=VagtSkifte.SKIFTE_1,
                holmen_double_nattevagt=False,
                holmen_dækselev_i_kabys=False,
                chronological_vagthavende=False,
                initial_vagthavende_first_shift=0,
                initial_vagthavende_second_shift=0,
                initial_vagthavende_third_shift=0,
            )
        )
        self.selected_vp_id = self.registry.vagtperioder[-1].id
        self.sync_form()
        self.sync_list()

    def remove_item(self) -> None:
        """Remove the selected item from the registry and sync the list and form"""
        if len(self.registry.vagtperioder) == 0:
            return

        if self.selected_vp_id is None:
            raise ValueError('Ingen vagtperiode valgt')

        vagtperiode = self.registry.get_vagtperiode_by_id(self.selected_vp_id)

        if vagtperiode is None:
            raise ValueError('Vagtperiode ikke fundet')

        self.registry.remove_vagtperiode(vagtperiode)

        self.selected_vp_id = self.registry.vagtperioder[-1].id if len(self.registry.vagtperioder) > 0 else None

        self.sync_form()
        self.sync_list()

    def _get_vp_index(self, vp_id: Optional[UUID]) -> Optional[int]:
        if vp_id is None:
            return None

        for i, vp in enumerate(self.registry.vagtperioder):
            if vp.id == vp_id:
                return i
        return None

    def on_update_registry(self) -> None:
        """Update the registry and sync the list and form"""
        self.sync_list()
        self.sync_form()
