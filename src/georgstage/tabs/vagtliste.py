import tkinter as tk
from tkinter import ttk
from georgstage.model import VagtTid, Opgave, VagtListe, Vagt
from georgstage.solver import autofill_vagtliste
from georgstage.util import EnhancedJSONEncoder
import json

class VagtListeTab(ttk.Frame):
    def __init__(self, parent, vagtlister: list[VagtListe], *args, **kwargs):
        ttk.Frame.__init__(self, parent, padding=(5, 5, 12, 0), *args, **kwargs)
        self.vcmd = self.register(lambda: False)

        self.table_header_var = tk.StringVar()
        self.vagtlister = vagtlister

        self.vagtliste_var = tk.Variable()
        self.vagtliste_listbox = tk.Listbox(
            self, listvariable=self.vagtliste_var, height=15, selectmode=tk.SINGLE
        )
        self.vagtliste_listbox.configure(exportselection=False)
        self.vagtliste_listbox.bind("<<ListboxSelect>>", self.on_select_list)
        self.selected_vagtliste_var: dict[tuple[VagtTid, Opgave], tk.StringVar] = {}

        self.vagtliste_listbox.grid(
            column=0, row=0, rowspan=19, sticky=(tk.N, tk.S, tk.E, tk.W)
        )

        ttk.Separator(self, orient=tk.VERTICAL).grid(
            column=1, row=0, rowspan=19, sticky="ns", padx=10
        )

        self.button_frame = ttk.Frame(self)

        self.save = ttk.Button(self.button_frame, text="Gem", command=self.save_action)
        self.autofill = ttk.Button(self.button_frame, text="Auto-Udfyld", command=self.autofill_action)
        self.clear = ttk.Button(self.button_frame, text="Ryd", command=self.clear_all)

        self.button_frame.grid(column=0, row=18, columnspan=10, sticky=tk.E, pady=5)
        self.save.grid(column=2, row=0)
        self.autofill.grid(column=1, row=0, padx=10)
        self.clear.grid(column=0, row=0)

        self.selected_index = 0
        self.sync_list()
        self.vagtliste_listbox.selection_set(0)
        self.grid_columnconfigure(0, weight=1)
        self.make_søvagt_table()

    def on_select_list(self, event):
        w = event.widget
        if len(w.curselection()) == 0:
            return
        index = int(w.curselection()[0])
        self.selected_index = index
        self.sync_list()
    
    def make_søvagt_table(self):
        vagt_opgaver = ["ELEV Vagtskifte", *Opgave._value2member_map_.keys()]
        vagt_tider = VagtTid._value2member_map_.keys()

        self.make_box(0, 0, "", 18, True, self.table_header_var)

        for index, opgave in enumerate(vagt_opgaver):
            self.make_box(index + 1, 0, opgave, 18, True)

        for index, time in enumerate(vagt_tider):
            self.make_box(0, index + 1, time, 8, True)

        for col, time in enumerate(vagt_tider):
            for row, opgave in enumerate(vagt_opgaver):
                self.selected_vagtliste_var[(time, opgave)] = tk.StringVar()
                self.make_box(
                    row + 1,
                    col + 1,
                    "",
                    8,
                    False,
                    self.selected_vagtliste_var[(time, opgave)],
                )

    def save_action(self):
        for (tid, opgave), sv in self.selected_vagtliste_var.items():
            if tid not in self.vagtlister[self.selected_index].vagter:
                self.vagtlister[self.selected_index].vagter[tid] = Vagt(1, {})
            self.vagtlister[self.selected_index].vagter[tid].opgaver[opgave] = sv.get()
        print(json.dumps(self.vagtlister[self.selected_index], indent=2, ensure_ascii=False, cls=EnhancedJSONEncoder))

    def sync_list(self):
        self.vagtliste_var.set(
            [
                f"{vagtliste.vagttype}: {vagtliste.start.strftime('%Y-%m-%d')}"
                for vagtliste in self.vagtlister
            ]
        )

        self.vagtliste_listbox.select_clear(0, tk.END)
        self.vagtliste_listbox.selection_set(self.selected_index)

        # Clear all string vars
        for sv in self.selected_vagtliste_var.values():
            sv.set("") 

        selected_vagtliste = self.vagtlister[self.selected_index]
        for time, vagt in selected_vagtliste.vagter.items():
            self.selected_vagtliste_var[(time), "ELEV Vagtskifte"].set(f"{vagt.vagt_skifte}#")
            for opgave, nr in vagt.opgaver.items():
                self.selected_vagtliste_var[(time, opgave.value)].set(nr)

        self.table_header_var.set(f"Søvagt: {self.vagtlister[self.selected_index].start.strftime('%Y-%m-%d')}")

        for i in range(0, len(self.vagtliste_var.get()), 2):
            self.vagtliste_listbox.itemconfigure(i, background="#f0f0ff")

    def on_edit(self, label, time):
        print(f"Got edit: {label}, {time}")

    def make_box(self, row, col, text, width, readonly, sv=None):
        entry1 = tk.Entry(
            self,
            textvariable=sv if sv is not None else tk.StringVar(self, value=text),
            width=width,
            **{"validatecommand": self.vcmd} if readonly else {},
        )
        entry1.update()
        entry1.configure(validate="key")
        entry1.grid(row=row, column=col + 2)
    
    def autofill_action(self):
        autofill_vagtliste(self.vagtlister[self.selected_index], self.vagtlister)
        self.sync_list()

    def clear_all(self):
        self.vagtlister[self.selected_index].vagter = {}
        self.sync_list()