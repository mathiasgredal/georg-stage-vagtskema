import tkinter as tk
from tkinter import ttk

from georgstage.model import Opgave, Vagt, VagtListe, VagtTid, VagtSkifte
from georgstage.solver import autofill_vagtliste
from georgstage.registry import Registry


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
        print('Registry changed')
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

        self.make_box(table_frame, 0, 0, '', 15, True, self.table_header_var)

        for index, opgave in enumerate(vagt_opgaver):
            self.make_box(table_frame, index + 1, 0, opgave.value, 15, True)

        for index, time in enumerate(vagt_tider):
            self.make_box(table_frame, 0, index + 1, time.value, 8, True)

        for col, time in enumerate(vagt_tider):
            for row, opgave in enumerate(vagt_opgaver):
                self.selected_vagtliste_var[(time, opgave)] = tk.StringVar()
                self.make_box(
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
            if tid not in self.registry.vagtlister[self.selected_index].vagter:
                self.registry.vagtlister[self.selected_index].vagter[tid] = Vagt(VagtSkifte.SKIFTE_1, {})
            if sv.get() == '':
                self.registry.vagtlister[self.selected_index].vagter[tid].opgaver.pop(opgave, None)
            else:
                self.registry.vagtlister[self.selected_index].vagter[tid].opgaver[opgave] = int(sv.get())

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

    def make_box(
        self, parent: tk.Misc, row: int, col: int, text: str, width: int, readonly: bool, sv: tk.StringVar | None = None
    ) -> None:
        entry1 = tk.Entry(
            parent,
            textvariable=sv if sv is not None else tk.StringVar(self, value=text),
            width=width,
            highlightthickness=0,
            borderwidth=1,
            relief='ridge',
        )
        if readonly:
            entry1.configure(validatecommand=self.vcmd)
            entry1.configure(takefocus=False)
            entry1.configure(state='disabled')
            entry1.configure(disabledbackground='white', disabledforeground='black')
        entry1.update()
        entry1.configure(validate='key')
        entry1.grid(row=row, column=col + 2)

    def autofill_action(self) -> None:
        self.save_action()
        autofill_vagtliste(self.registry.vagtlister[self.selected_index], self.registry.vagtlister)
        self.sync_list()

    def clear_all(self) -> None:
        self.registry.vagtlister[self.selected_index].vagter = {}
        self.sync_list()
