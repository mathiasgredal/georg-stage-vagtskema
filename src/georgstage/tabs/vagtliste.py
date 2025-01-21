import tkinter as tk
from tkinter import ttk
from typing import Optional

from georgstage.components.tooltip import ToolTip
from georgstage.model import HU, Opgave, Vagt, VagtTid, VagtType
from georgstage.solver import autofill_vagtliste
from georgstage.registry import Registry
from georgstage.util import make_cell
from georgstage.validator import show_validation_error, validate_hu, validate_vagtliste
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
        self.hu_var: list[tk.StringVar] = []

        # GUI Elements
        self.vagtliste_listbox = tk.Listbox(self, listvariable=self.vagtliste_var, height=15, selectmode=tk.SINGLE)
        self.vagtliste_listbox.configure(exportselection=False)
        self.vagtliste_listbox.bind('<<ListboxSelect>>', self.on_select_list)

        self.autofill_all_frm = tk.Frame(self.vagtliste_listbox, background='white', width=25, height=25)
        self.autofill_all_btn = ttk.Button(
            self.autofill_all_frm, text=' ↻', command=self.on_autofill_all, style='Danger.TButton'
        )
        self.autofill_all_btn_ttp = ToolTip(self.autofill_all_btn, 'Genskab alle vagter')

        self.vert_sep = ttk.Separator(self, orient=tk.VERTICAL)

        self.action_btns = ttk.Frame(self)
        self.save_btn = ttk.Button(self.action_btns, text='Anvend', command=self.save_action)
        self.autofill_btn = ttk.Button(self.action_btns, text='Auto-Udfyld', command=self.autofill_action)
        self.clear_btn = ttk.Button(self.action_btns, text='Ryd', command=self.clear_all)

        self.ude_label = ttk.Label(self.action_btns, text='Ude: ')
        self.ude_var = tk.StringVar()
        self.ude_entry = ttk.Entry(self.action_btns, textvariable=self.ude_var)

        self.søvagt_table_frame = self.make_søvagt_table()
        self.havnevagt_table_frame = self.make_havnevagt_table()
        self.holmen_table_frame = self.make_holmen_table()

        # Layout
        self.vagtliste_listbox.grid(column=0, row=0, rowspan=2, sticky='nsew')

        self.autofill_all_frm.grid(column=1, row=1, pady=5, padx=5, sticky='nsew')
        self.autofill_all_frm.grid_propagate(False)
        self.autofill_all_frm.grid_columnconfigure(0, weight=1)
        self.autofill_all_frm.grid_rowconfigure(0, weight=1)
        self.autofill_all_btn.grid(sticky='nsew')

        self.vagtliste_listbox.grid_columnconfigure(0, weight=1)
        self.vagtliste_listbox.grid_rowconfigure(0, weight=1)

        self.vert_sep.grid(column=1, row=0, rowspan=2, sticky='ns', padx=10)

        self.ude_label.pack(side='left', padx=5)
        self.ude_entry.pack(side='left', padx=(5, 30))

        self.save_btn.pack(side='right', padx=(5, 0))
        self.autofill_btn.pack(side='right', padx=5)
        self.clear_btn.pack(side='right', padx=5)
        self.action_btns.grid(column=2, row=1, sticky='ew', pady=5)
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

    def on_autofill_all(self) -> None:
        old_selected_index = self.selected_index
        self.registry.vagtlister = []
        for vagtperiode in self.registry.vagtperioder:
            self.registry.update_vagtperiode(vagtperiode.id, vagtperiode, notify=False)
        self.selected_index = old_selected_index
        self.registry.notify_update_listeners()

    def make_holmen_table(self) -> ttk.Frame:
        table_frame = ttk.Frame(self)

        holmen_vagt_tider = [
            VagtTid.ALL_DAY,
            VagtTid.T22_00,
            VagtTid.T00_02,
            VagtTid.T02_04,
            VagtTid.T04_06,
            VagtTid.T06_08,
        ]

        make_cell(table_frame, 0, 0, '', 15, True, self.table_header_var)

        make_cell(table_frame, 1, 0, Opgave.NATTEVAGT_A.value, 15, True)
        make_cell(table_frame, 2, 0, Opgave.NATTEVAGT_B.value, 15, True)


        for index, time in enumerate(holmen_vagt_tider):
            if time == VagtTid.ALL_DAY:
                continue
            make_cell(table_frame, 0, index + 1, time.value, 5, True)

        for col, time in enumerate(holmen_vagt_tider):
            if time == VagtTid.ALL_DAY:
                continue
            for row, opgave in enumerate([Opgave.NATTEVAGT_A, Opgave.NATTEVAGT_B]):
                self.holmen_vagtliste_var[(time, opgave)] = tk.StringVar()
                make_cell(
                    table_frame,
                    row + 1,
                    col + 1,
                    '',
                    5,
                    False,
                    self.holmen_vagtliste_var[(time, opgave)],
                )

        self.holmen_vagtliste_var[(VagtTid.ALL_DAY, Opgave.ELEV_VAGTSKIFTE)] = tk.StringVar()
        make_cell(table_frame, 4, 0, 'ELEV vagtskifte', 15, True, pady=(5, 0))
        make_cell(
            table_frame,
            4,
            1,
            '',
            15,
            False,
            self.holmen_vagtliste_var[(VagtTid.ALL_DAY, Opgave.ELEV_VAGTSKIFTE)],
            pady=(5, 0),
            columnspan=4,
            sticky='w',
        )

        self.holmen_vagtliste_var[(VagtTid.ALL_DAY, Opgave.VAGTHAVENDE_ELEV)] = tk.StringVar()
        make_cell(
            table_frame,
            5,
            0,
            'Vagthavende ELEV',
            15,
            True,
        )
        make_cell(
            table_frame,
            5,
            1,
            '',
            15,
            False,
            self.holmen_vagtliste_var[(VagtTid.ALL_DAY, Opgave.VAGTHAVENDE_ELEV)],
            columnspan=4,
            sticky='w',
        )

        self.holmen_vagtliste_var[(VagtTid.ALL_DAY, Opgave.DAEKSELEV_I_KABYS)] = tk.StringVar()
        make_cell(
            table_frame,
            6,
            0,
            'Dækselev i kabys',
            15,
            True,
        )
        make_cell(
            table_frame,
            6,
            1,
            '',
            15,
            False,
            self.holmen_vagtliste_var[(VagtTid.ALL_DAY, Opgave.DAEKSELEV_I_KABYS)],
            columnspan=4,
            sticky='w',
        )

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

        make_cell(table_frame, 4, 0, 'HU', 15, True, pady=(5, 0))
        for i in range(2, 10, 2):
            self.hu_var.append(tk.StringVar())
            make_cell(table_frame, 4, i, '', 10, False, self.hu_var[-1], columnspan=2, ipadx=2, pady=(5, 0), sticky='w')
            self.hu_var.append(tk.StringVar())
            make_cell(table_frame, 5, i, '', 10, False, self.hu_var[-1], columnspan=2, ipadx=2, sticky='w')

        self.havnevagt_vagtliste_var[(VagtTid.ALL_DAY, Opgave.ELEV_VAGTSKIFTE)] = tk.StringVar()
        make_cell(table_frame, 6, 0, 'ELEV vagtskifte', 15, True, pady=(5, 0))
        make_cell(
            table_frame,
            6,
            1,
            '',
            15,
            True,
            self.havnevagt_vagtliste_var[(VagtTid.ALL_DAY, Opgave.ELEV_VAGTSKIFTE)],
            pady=(5, 0),
            columnspan=4,
            sticky='w',
        )

        self.havnevagt_vagtliste_var[(VagtTid.ALL_DAY, Opgave.VAGTHAVENDE_ELEV)] = tk.StringVar()
        make_cell(table_frame, 7, 0, 'Vagthavende ELEV', 15, True)
        make_cell(
            table_frame,
            7,
            1,
            '',
            15,
            False,
            self.havnevagt_vagtliste_var[(VagtTid.ALL_DAY, Opgave.VAGTHAVENDE_ELEV)],
            columnspan=4,
            sticky='w',
        )

        self.havnevagt_vagtliste_var[(VagtTid.ALL_DAY, Opgave.DAEKSELEV_I_KABYS)] = tk.StringVar()
        make_cell(table_frame, 8, 0, 'Dækselev i kabys', 15, True)
        make_cell(
            table_frame,
            8,
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
        if len(self.registry.vagtlister) == 0:
            return
        
        self.vagtliste_var.set([vagtliste.to_string() for vagtliste in self.registry.vagtlister])

        if self.selected_index >= len(self.registry.vagtlister):
            self.selected_index = len(self.registry.vagtlister) - 1

        self.vagtliste_listbox.select_clear(0, tk.END)
        self.vagtliste_listbox.selection_set(self.selected_index)

        for i in range(0, len(self.vagtliste_var.get()), 2):  # type: ignore
            self.vagtliste_listbox.itemconfigure(i, background='#f0f0ff')

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
            f"{selected_vagtliste.vagttype.value}: {selected_vagtliste.get_date().strftime('%Y-%m-%d')}"
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

        if selected_vagtliste.vagter != {}:
            found_hu: Optional[HU] = None
            for hu in self.registry.hu:
                if (
                    hu.start_date == selected_vagtliste.start.date()
                    and selected_vagtliste.vagttype == VagtType.HAVNEVAGT
                ):
                    found_hu = hu
                    break

            if found_hu is not None:
                for i, sv in enumerate(self.hu_var):
                    if i >= len(found_hu.assigned):
                        break
                    if found_hu.assigned[i] != 0:
                        sv.set(str(found_hu.assigned[i]))
                    else:
                        sv.set('')
            else:
                for sv in self.hu_var:
                    sv.set('')

        self.table_header_var.set(
            f"{selected_vagtliste.vagttype.value}: {selected_vagtliste.start.strftime('%Y-%m-%d')}"
        )
        return

    def sync_holmen_table(self) -> None:
        selected_vagtliste = self.registry.vagtlister[self.selected_index]
        for sv in self.holmen_vagtliste_var.values():
            sv.set('')

        for (tid, opgave), sv in self.holmen_vagtliste_var.items():
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

    def save_holmen(self) -> None:
        for (tid, opgave), sv in self.holmen_vagtliste_var.items():
            if opgave == Opgave.ELEV_VAGTSKIFTE:
                continue

            selected_vagtliste = self.registry.vagtlister[self.selected_index]

            if tid not in selected_vagtliste.vagter:
                continue

            unvalidated_vagtliste = deepcopy(selected_vagtliste)
            if tid not in unvalidated_vagtliste.vagter:
                unvalidated_vagtliste.vagter[tid] = Vagt(unvalidated_vagtliste.starting_shift, {})
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

    def save_havnevagt(self) -> None:
        selected_vagtliste = self.registry.vagtlister[self.selected_index]
        unvalidated_vagtliste = deepcopy(selected_vagtliste)

        for (tid, opgave), sv in self.havnevagt_vagtliste_var.items():
            if opgave == Opgave.ELEV_VAGTSKIFTE:
                continue

            if tid not in selected_vagtliste.vagter:
                continue

            if tid not in unvalidated_vagtliste.vagter:
                unvalidated_vagtliste.vagter[tid] = Vagt(unvalidated_vagtliste.starting_shift, {})
            if sv.get() == '':
                unvalidated_vagtliste.vagter[tid].opgaver.pop(opgave, None)
            else:
                unvalidated_vagtliste.vagter[tid].opgaver[opgave] = int(sv.get())

        validation_result = validate_vagtliste(unvalidated_vagtliste)
        if validation_result is not None:
            show_validation_error(validation_result)
            return
        else:
            self.registry.vagtlister[self.selected_index] = unvalidated_vagtliste

        selected_vagtliste = self.registry.vagtlister[self.selected_index]
        found_hu: Optional[HU] = None
        for hu in self.registry.hu:
            if hu.start_date == selected_vagtliste.start.date() and selected_vagtliste.vagttype == VagtType.HAVNEVAGT:
                found_hu = hu
                break

        if found_hu is None:
            found_hu = HU(selected_vagtliste.start.date(), [])
            self.registry.hu.append(found_hu)

        found_hu.assigned = [0 if sv.get() == '' else int(sv.get()) for sv in self.hu_var]

        validation_result = validate_hu(selected_vagtliste, found_hu)
        if validation_result is not None:
            show_validation_error(validation_result)
            return

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
        # Parse the comma separated list of elev nrs in ude_var
        try:
            ude_nrs = [int(nr) for nr in self.ude_var.get().split(',') if nr != '']
        except:
            mb.showerror('Fejl', 'Ude elev numre skal være kommasepareret, f.eks. 12, 43')
            return
        self.save_action()
        autofill_vagtliste(self.registry.vagtlister[self.selected_index], self.registry, ude_nrs)
        self.sync_list()

    def clear_all(self) -> None:
        self.registry.vagtlister[self.selected_index].vagter = {}
        self.sync_list()
