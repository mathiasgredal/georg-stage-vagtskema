import tkinter as tk
from tkinter import ttk

from georgstage.model import Opgave, Vagt, VagtListe, VagtTid, VagtSkifte, VagtType
from georgstage.solver import autofill_vagtliste, søvagt_skifte_for_vagttid
from georgstage.registry import Registry
from georgstage.util import make_cell
from georgstage.validator import validate_vagtliste
from tkinter import messagebox as mb
from copy import deepcopy

class VagtListeTab(ttk.Frame):
    def __init__(self, parent: tk.Misc, registry: Registry) -> None:
        ttk.Frame.__init__(self, parent, padding=(5, 5, 12, 5))
        self.registry = registry
        self.vcmd = self.register(lambda: False)

        # State variables
        self.table_header_var = tk.StringVar()
        self.vagtliste_var = tk.Variable()

        # Create a vagtlist var for each vagttype: søvagt, havnevagt, holmen
        self.søvagt_vagtliste_var: dict[tuple[VagtTid, Opgave], tk.StringVar] = {}
        self.havnevagt_vagtliste_var: dict[tuple[VagtTid, Opgave], tk.StringVar] = {}
        self.holmen_vagtliste_var: dict[tuple[VagtTid, Opgave], tk.StringVar] = {}

        # GUI Elements
        self.vagtliste_listbox = tk.Listbox(self, listvariable=self.vagtliste_var, height=15, selectmode=tk.SINGLE)
        self.vagtliste_listbox.configure(exportselection=False)
        self.vagtliste_listbox.bind('<<ListboxSelect>>', self.on_select_list)

        self.vert_sep = ttk.Separator(self, orient=tk.VERTICAL)

        self.action_btns = ttk.Frame(self)
        self.save_btn = ttk.Button(self.action_btns, text='Gem', command=self.save_action)
        self.autofill_btn = ttk.Button(self.action_btns, text='Auto-Udfyld', command=self.autofill_action)
        self.clear_btn = ttk.Button(self.action_btns, text='Ryd', command=self.clear_all)

        self.søvagt_table_frame = self.make_søvagt_table()
        self.havnevagt_table_frame = self.make_havnevagt_table()
        self.holmen_table_frame = self.make_holmen_table()

        # Layout
        self.vagtliste_listbox.grid(column=0, row=0, rowspan=2, sticky='nsew')
        self.vert_sep.grid(column=1, row=0, rowspan=2, sticky='ns', padx=10)

        self.save_btn.grid(column=2, row=0)
        self.autofill_btn.grid(column=1, row=0, padx=10)
        self.clear_btn.grid(column=0, row=0)
        self.action_btns.grid(column=0, row=1, columnspan=3, sticky=tk.E, pady=5)
        self.søvagt_table_frame.grid(column=2, row=0, sticky='nsew')

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.selected_index = 0
        self.sync_list()
        self.vagtliste_listbox.selection_set(self.selected_index)
        self.registry.register_update_listener(self.on_registry_change)

    def on_select_list(self, event: tk.Event) -> None:  # type: ignore
        w = event.widget
        if len(w.curselection()) == 0:
            return
        index = int(w.curselection()[0])
        self.selected_index = index
        self.sync_list()

    def on_registry_change(self) -> None:
        self.sync_list()

    def make_holmen_table(self) -> ttk.Frame:
        table_frame = ttk.Frame(self)
        return table_frame

    def make_havnevagt_table(self) -> ttk.Frame:
        table_frame = ttk.Frame(self)

        havne_vagt_tider = [
            VagtTid.ALL_DAY,
            VagtTid.T08_12,
            VagtTid.T12_16,
            VagtTid.T16_18,
            VagtTid.T18_20,
            VagtTid.T20_22,
            VagtTid.T22_00,
            VagtTid.T00_02,
            VagtTid.T02_04,
            VagtTid.T04_06,
            VagtTid.T06_08,
        ]

        make_cell(table_frame, 0, 0, '', 15, True, self.table_header_var)

        for index, opgave in enumerate([Opgave.LANDGANGSVAGT_A, Opgave.LANDGANGSVAGT_B]):
            make_cell(table_frame, index + 1, 0, opgave.value, 15, True)

        for index, time in enumerate(havne_vagt_tider):
            if time == VagtTid.ALL_DAY:
                continue
            make_cell(table_frame, 0, index + 1, time.value, 5, True)

        for col, time in enumerate(havne_vagt_tider):
            if time == VagtTid.ALL_DAY:
                continue
            for row, opgave in enumerate([Opgave.LANDGANGSVAGT_A, Opgave.LANDGANGSVAGT_B]):
                self.havnevagt_vagtliste_var[(time, opgave)] = tk.StringVar()
                make_cell(
                    table_frame,
                    row + 1,
                    col + 1,
                    '',
                    5,
                    False,
                    self.havnevagt_vagtliste_var[(time, opgave)],
                )

        self.havnevagt_vagtliste_var[(VagtTid.ALL_DAY, Opgave.ELEV_VAGTSKIFTE)] = tk.StringVar()
        make_cell(table_frame, 4, 0, 'ELEV vagtskifte', 15, False, pady=(5, 0))
        make_cell(
            table_frame,
            4,
            1,
            '',
            15,
            False,
            self.havnevagt_vagtliste_var[(VagtTid.ALL_DAY, Opgave.ELEV_VAGTSKIFTE)],
            pady=(5, 0),
            columnspan=4,
            sticky='w',
        )

        self.havnevagt_vagtliste_var[(VagtTid.ALL_DAY, Opgave.VAGTHAVENDE_ELEV)] = tk.StringVar()
        make_cell(
            table_frame,
            5,
            0,
            'Vagthavende ELEV',
            15,
            False,
        )
        make_cell(
            table_frame,
            5,
            1,
            '',
            15,
            False,
            self.havnevagt_vagtliste_var[(VagtTid.ALL_DAY, Opgave.VAGTHAVENDE_ELEV)],
            columnspan=4,
            sticky='w',
        )

        self.havnevagt_vagtliste_var[(VagtTid.ALL_DAY, Opgave.DAEKSELEV_I_KABYS)] = tk.StringVar()
        make_cell(
            table_frame,
            6,
            0,
            'Dækselev i kabys',
            15,
            False,
        )
        make_cell(
            table_frame,
            6,
            1,
            '',
            15,
            False,
            self.havnevagt_vagtliste_var[(VagtTid.ALL_DAY, Opgave.DAEKSELEV_I_KABYS)],
            columnspan=4,
            sticky='w',
        )
        return table_frame

    def make_søvagt_table(self) -> ttk.Frame:
        table_frame = ttk.Frame(self)
        vagt_opgaver = [
            Opgave.ELEV_VAGTSKIFTE,
            Opgave.VAGTHAVENDE_ELEV,
            Opgave.ORDONNANS,
            Opgave.UDKIG,
            Opgave.RADIOVAGT,
            Opgave.RORGAENGER,
            Opgave.UDSAETNINGSGAST_A,
            Opgave.UDSAETNINGSGAST_B,
            Opgave.UDSAETNINGSGAST_C,
            Opgave.UDSAETNINGSGAST_D,
            Opgave.UDSAETNINGSGAST_E,
            Opgave.PEJLEGAST_A,
            Opgave.PEJLEGAST_B,
            Opgave.DAEKSELEV_I_KABYS,
        ]

        vagt_tider = [
            VagtTid.T08_12,
            VagtTid.T12_15,
            VagtTid.T15_20,
            VagtTid.T20_24,
            VagtTid.T00_04,
            VagtTid.T04_08,
        ]

        make_cell(table_frame, 0, 0, '', 15, True, self.table_header_var)

        for index, opgave in enumerate(vagt_opgaver):
            make_cell(table_frame, index + 1, 0, opgave.value, 15, True)

        for index, time in enumerate(vagt_tider):
            make_cell(table_frame, 0, index + 1, time.value, 8, True)

        for col, time in enumerate(vagt_tider):
            for row, opgave in enumerate(vagt_opgaver):
                self.søvagt_vagtliste_var[(time, opgave)] = tk.StringVar()
                make_cell(
                    table_frame,
                    row + 1,
                    col + 1,
                    '',
                    8,
                    False,
                    self.søvagt_vagtliste_var[(time, opgave)],
                )

        return table_frame

    def save_action(self) -> None:
        if self.registry.vagtlister[self.selected_index].vagttype == VagtType.SOEVAGT:
            self.save_søvagt()
        elif self.registry.vagtlister[self.selected_index].vagttype == VagtType.HAVNEVAGT:
            self.save_havnevagt()
        elif self.registry.vagtlister[self.selected_index].vagttype == VagtType.HOLMEN:
            self.save_holmen()
        self.registry.notify_update_listeners()

    def sync_list(self) -> None:
        # Update the listbox
        self.vagtliste_var.set([vagtliste.to_string() for vagtliste in self.registry.vagtlister])

        if self.selected_index >= len(self.registry.vagtlister):
            self.selected_index = len(self.registry.vagtlister) - 1

        self.vagtliste_listbox.select_clear(0, tk.END)
        self.vagtliste_listbox.selection_set(self.selected_index)

        for i in range(0, len(self.vagtliste_var.get()), 2):  # type: ignore
            self.vagtliste_listbox.itemconfigure(i, background='#f0f0ff')

        if len(self.registry.vagtlister) == 0:
            return

        # Display the correct table
        if self.registry.vagtlister[self.selected_index].vagttype == VagtType.SOEVAGT:
            self.havnevagt_table_frame.grid_forget()
            self.holmen_table_frame.grid_forget()
            self.søvagt_table_frame.grid(column=2, row=0, sticky='nsew')
            self.sync_søvagt_table()
        elif self.registry.vagtlister[self.selected_index].vagttype == VagtType.HAVNEVAGT:
            self.holmen_table_frame.grid_forget()
            self.søvagt_table_frame.grid_forget()
            self.havnevagt_table_frame.grid(column=2, row=0, sticky='nsew')
            self.sync_havnevagt_table()
        elif self.registry.vagtlister[self.selected_index].vagttype == VagtType.HOLMEN:
            self.havnevagt_table_frame.grid_forget()
            self.søvagt_table_frame.grid_forget()
            self.holmen_table_frame.grid(column=2, row=0, sticky='nsew')
            self.sync_holmen_table()

    def sync_søvagt_table(self) -> None:
        for sv in self.søvagt_vagtliste_var.values():
            sv.set('')

        selected_vagtliste = self.registry.vagtlister[self.selected_index]

        for time, vagt in selected_vagtliste.vagter.items():
            if (time, Opgave.ELEV_VAGTSKIFTE) in self.søvagt_vagtliste_var:
                self.søvagt_vagtliste_var[(time, Opgave.ELEV_VAGTSKIFTE)].set(f'{vagt.vagt_skifte.value}#')
            for opgave, nr in vagt.opgaver.items():
                self.søvagt_vagtliste_var[(time, opgave)].set(str(nr))

        self.table_header_var.set(
            f"{selected_vagtliste.vagttype.value}: {selected_vagtliste.start.strftime('%Y-%m-%d')}"
        )

    def sync_havnevagt_table(self) -> None:
        selected_vagtliste = self.registry.vagtlister[self.selected_index]

        for sv in self.havnevagt_vagtliste_var.values():
            sv.set('')

        for (tid, opgave), sv in self.havnevagt_vagtliste_var.items():
            if opgave == Opgave.ELEV_VAGTSKIFTE:
                sv.set(f'{selected_vagtliste.starting_shift.value}#')
                continue

            if tid not in selected_vagtliste.vagter:
                continue

            if opgave in selected_vagtliste.vagter[tid].opgaver:
                sv.set(str(selected_vagtliste.vagter[tid].opgaver[opgave]))

        self.table_header_var.set(
            f"{selected_vagtliste.vagttype.value}: {selected_vagtliste.start.strftime('%Y-%m-%d')}"
        )
        return

    def sync_holmen_table(self) -> None:
        return

    def save_havnevagt(self) -> None:
        for (tid, opgave), sv in self.havnevagt_vagtliste_var.items():
            if opgave == Opgave.ELEV_VAGTSKIFTE:
                continue

            selected_vagtliste = self.registry.vagtlister[self.selected_index]

            if tid not in selected_vagtliste.vagter:
                continue
            
            unvalidated_vagtliste = deepcopy(selected_vagtliste)
            if tid not in unvalidated_vagtliste.vagter:
                skifte = søvagt_skifte_for_vagttid(unvalidated_vagtliste.starting_shift, tid)
                unvalidated_vagtliste.vagter[tid] = Vagt(skifte, {})
            if sv.get() == '':
                unvalidated_vagtliste.vagter[tid].opgaver.pop(opgave, None)
            else:
                unvalidated_vagtliste.vagter[tid].opgaver[opgave] = int(sv.get())

            validation_result = validate_vagtliste(unvalidated_vagtliste)
            if validation_result is not None:
                mb.showerror(
                    'Fejl',
                    f'Fejl i vagtliste({validation_result.vagttid.value}) - {validation_result.conflict_a[0].value} og {validation_result.conflict_b[0].value} har samme elev nr. {validation_result.conflict_a[1]}',
                )
                return
            else:
                self.registry.vagtlister[self.selected_index] = unvalidated_vagtliste

    def save_søvagt(self) -> None:
        selected_vagtliste = self.registry.vagtlister[self.selected_index]
        unvalidated_vagtliste = deepcopy(selected_vagtliste)

        for (tid, opgave), sv in self.søvagt_vagtliste_var.items():
            if opgave == Opgave.ELEV_VAGTSKIFTE:
                continue

            if tid not in selected_vagtliste.vagter:
                continue

            if sv.get() == '':
                unvalidated_vagtliste.vagter[tid].opgaver.pop(opgave, None)
            else:
                unvalidated_vagtliste.vagter[tid].opgaver[opgave] = int(sv.get())

        validation_result = validate_vagtliste(unvalidated_vagtliste)
        if validation_result is not None:
            mb.showerror(
                'Fejl',
                f'Fejl i vagtliste({validation_result.vagttid.value}) - {validation_result.conflict_a[0].value} og {validation_result.conflict_b[0].value} har samme elev nr. {validation_result.conflict_a[1]}',
            )
            return
        else:
            self.registry.vagtlister[self.selected_index] = unvalidated_vagtliste

    def autofill_action(self) -> None:
        self.save_action()
        autofill_vagtliste(self.registry.vagtlister[self.selected_index], self.registry)
        self.sync_list()

    def clear_all(self) -> None:
        self.registry.vagtlister[self.selected_index].vagter = {}
        self.sync_list()
