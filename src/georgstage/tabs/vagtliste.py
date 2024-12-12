import tkinter as tk
from tkinter import ttk

from georgstage.model import Opgave, Vagt, VagtListe, VagtTid, VagtSkifte
from georgstage.solver import autofill_vagtliste, søvagt_skifte_for_vagttid
from georgstage.registry import Registry
from georgstage.util import make_cell
from georgstage.validator import validate_vagtliste
from pydantic import TypeAdapter
from tkinter import messagebox as mb

class VagtListeTab(ttk.Frame):
    def __init__(self, parent: tk.Misc, registry: Registry) -> None:
        ttk.Frame.__init__(self, parent, padding=(5, 5, 12, 5))
        self.registry = registry
        self.vcmd = self.register(lambda: False)

        # State variables
        self.table_header_var = tk.StringVar()
        self.vagtliste_var = tk.Variable()
        self.selected_vagtliste_var: dict[tuple[VagtTid, Opgave], tk.StringVar] = {}

        # GUI Elements
        self.vagtliste_listbox = tk.Listbox(self, listvariable=self.vagtliste_var, height=15, selectmode=tk.SINGLE)
        self.vagtliste_listbox.configure(exportselection=False)
        self.vagtliste_listbox.bind('<<ListboxSelect>>', self.on_select_list)

        self.vert_sep = ttk.Separator(self, orient=tk.VERTICAL)

        self.action_btns = ttk.Frame(self)
        self.save_btn = ttk.Button(self.action_btns, text='Gem', command=self.save_action)
        self.autofill_btn = ttk.Button(self.action_btns, text='Auto-Udfyld', command=self.autofill_action)
        self.clear_btn = ttk.Button(self.action_btns, text='Ryd', command=self.clear_all)

        self.table_frame = self.make_søvagt_table()

        # Layout
        self.vagtliste_listbox.grid(column=0, row=0, rowspan=2, sticky='nsew')
        self.vert_sep.grid(column=1, row=0, rowspan=2, sticky='ns', padx=10)
        self.table_frame.grid(column=2, row=0, sticky='nsew')

        self.save_btn.grid(column=2, row=0)
        self.autofill_btn.grid(column=1, row=0, padx=10)
        self.clear_btn.grid(column=0, row=0)
        self.action_btns.grid(column=0, row=1, columnspan=3, sticky=tk.E, pady=5)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)
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
                self.selected_vagtliste_var[(time, opgave)] = tk.StringVar()
                make_cell(
                    table_frame,
                    row + 1,
                    col + 1,
                    '',
                    8,
                    False,
                    self.selected_vagtliste_var[(time, opgave)],
                )

        return table_frame

    def save_action(self) -> None:
        for (tid, opgave), sv in self.selected_vagtliste_var.items():
            if opgave == Opgave.ELEV_VAGTSKIFTE:
                continue

            selected_vagtliste = self.registry.vagtlister[self.selected_index]

            if tid not in selected_vagtliste.vagter:
                continue
            unvalidated_vagtliste = TypeAdapter(VagtListe).validate_json(TypeAdapter(VagtListe).dump_json(selected_vagtliste))
            if tid not in unvalidated_vagtliste.vagter:
                skifte = søvagt_skifte_for_vagttid(unvalidated_vagtliste.starting_shift, tid)
                unvalidated_vagtliste.vagter[tid] = Vagt(skifte, {})
            if sv.get() == '':
                unvalidated_vagtliste.vagter[tid].opgaver.pop(opgave, None)
            else:
                unvalidated_vagtliste.vagter[tid].opgaver[opgave] = int(sv.get())
            
            validation_result = validate_vagtliste(unvalidated_vagtliste)
            if validation_result is not None:
                mb.showerror('Fejl', f'Fejl i vagtliste({validation_result.vagttid.value}) - {validation_result.conflict_a[0].value} og {validation_result.conflict_b[0].value} har samme elev nr. {validation_result.conflict_a[1]}')
                return
            else:
                self.registry.vagtlister[self.selected_index] = unvalidated_vagtliste

    def sync_list(self) -> None:
        self.vagtliste_var.set(
            [
                f"{vagtliste.vagttype.value}: {vagtliste.start.strftime('%Y-%m-%d')}"
                for vagtliste in self.registry.vagtlister
            ]
        )

        self.vagtliste_listbox.select_clear(0, tk.END)
        self.vagtliste_listbox.selection_set(self.selected_index)

        # Clear all string vars
        for sv in self.selected_vagtliste_var.values():
            sv.set('')

        if len(self.registry.vagtlister) != 0:
            if self.selected_index >= len(self.registry.vagtlister):
                self.selected_index = len(self.registry.vagtlister) - 1
            selected_vagtliste = self.registry.vagtlister[self.selected_index]
            for time, vagt in selected_vagtliste.vagter.items():
                self.selected_vagtliste_var[(time, Opgave.ELEV_VAGTSKIFTE)].set(f'{vagt.vagt_skifte.value}#')
                for opgave, nr in vagt.opgaver.items():
                    self.selected_vagtliste_var[(time, opgave)].set(str(nr))

            self.table_header_var.set(
                f"{selected_vagtliste.vagttype.value}: {selected_vagtliste.start.strftime('%Y-%m-%d')}"
            )

        for i in range(0, len(self.vagtliste_var.get()), 2):  # type: ignore
            self.vagtliste_listbox.itemconfigure(i, background='#f0f0ff')

    def autofill_action(self) -> None:
        self.save_action()
        autofill_vagtliste(self.registry.vagtlister[self.selected_index], self.registry.vagtlister)
        self.sync_list()

    def clear_all(self) -> None:
        self.registry.vagtlister[self.selected_index].vagter = {}
        self.sync_list()
