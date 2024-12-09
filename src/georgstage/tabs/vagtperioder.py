import tkinter as tk
from tkinter import ttk
from georgstage.model import VagtPeriode
from datetime import datetime

class VagtPeriodeTab(ttk.Frame):
    def __init__(
        self, parent, vagtperioder: list[VagtPeriode], on_save, *args, **kwargs
    ):
        ttk.Frame.__init__(self, parent, padding=(5, 5, 12, 0), *args, **kwargs)

        self.vagtperioder = vagtperioder
        self.on_save = on_save
        # State variables
        self.vagtperiode_type = tk.StringVar()
        self.selected_shift = tk.StringVar()
        self.vagtperioder_var = tk.Variable()
        self.note_var = tk.Variable()

        self.vagtperioder_listbox = tk.Listbox(
            self, listvariable=self.vagtperioder_var, height=15, selectmode=tk.SINGLE
        )
        self.vagtperioder_listbox.bind("<<ListboxSelect>>", self.on_select_period)

        # Vagtperiode Form
        self.type_label = ttk.Label(self, text="Type af vagtperiode:")
        self.type_opt1 = ttk.Radiobutton(
            self, text="Søvagt", variable=self.vagtperiode_type, value="Søvagt"
        )
        self.type_opt2 = ttk.Radiobutton(
            self, text="Havnevagt", variable=self.vagtperiode_type, value="Havnevagt"
        )
        self.type_opt3 = ttk.Radiobutton(
            self, text="Ankervagt", variable=self.vagtperiode_type, value="Ankervagt"
        )
        self.type_opt4 = ttk.Radiobutton(
            self, text="Holmen", variable=self.vagtperiode_type, value="Holmen"
        )

        self.startdate_label = ttk.Label(self, text="Start:")
        self.startdate_var = tk.StringVar()
        self.startdate_entry = ttk.Entry(self, textvariable=self.startdate_var)

        self.enddate_label = ttk.Label(self, text="Slut:")
        self.enddate_var = tk.StringVar()
        self.enddate_entry = ttk.Entry(self, textvariable=self.enddate_var)

        self.vagttørn_label = ttk.Label(self, text="Vagttørn:")
        self.vagttørn_entry = ttk.Combobox(
            self, width=10, textvariable=self.selected_shift
        )
        self.vagttørn_entry["values"] = (" 1#", " 2#", " 3#")
        self.vagttørn_entry.current(0)

        self.note_label = ttk.Label(self, text="Note:")
        self.note_entry = ttk.Entry(self, textvariable=self.note_var)

        self.add_remove_frame = ttk.Frame(self)
        self.add = ttk.Button(
            self.add_remove_frame, text="Tilføj...", command=self.add_item
        )
        self.remove = ttk.Button(
            self.add_remove_frame, text="Fjern", command=self.remove_item
        )
        self.send = ttk.Button(
            self, text="Gem", default="active", command=self.save_action
        )

        # Grid all the widgets
        self.vagtperioder_listbox.grid(
            column=0, row=0, rowspan=13, sticky=(tk.N, tk.S, tk.E, tk.W)
        )

        self.type_label.grid(column=1, row=0, sticky=tk.W, padx=10, pady=5)
        self.type_opt1.grid(column=1, row=1, sticky=tk.W, padx=20)
        self.type_opt2.grid(column=1, row=2, sticky=tk.W, padx=20)
        self.type_opt3.grid(column=1, row=3, sticky=tk.W, padx=20)
        self.type_opt4.grid(column=1, row=4, sticky=tk.W, padx=20)

        self.startdate_label.grid(column=1, row=5, sticky=tk.W, padx=10)
        self.startdate_entry.grid(column=1, row=6, sticky=tk.W, padx=20)

        self.enddate_label.grid(column=1, row=7, sticky=tk.W, padx=10)
        self.enddate_entry.grid(column=1, row=8, sticky=tk.W, padx=20)

        self.vagttørn_label.grid(column=1, row=9, sticky=tk.W, padx=10)
        self.vagttørn_entry.grid(column=1, row=10, sticky=tk.W, padx=20)

        self.note_label.grid(column=1, row=11, sticky=tk.W, padx=10)
        self.note_entry.grid(column=1, row=12, sticky=tk.W, padx=20)

        self.send.grid(
            column=2,
            row=14,
            pady=10,
        )
        self.add_remove_frame.grid(column=0, row=14, columnspan=2, sticky=(tk.W, tk.E))

        self.add.grid(column=0, row=1, sticky=(tk.W))
        self.remove.grid(column=1, row=1, sticky=(tk.W), padx=10)

        # Make the listbox column expand
        self.grid_columnconfigure(0, weight=1)
        
        # Select the first item
        self.selected_index = 0
        self.sync_form()
        self.sync_list()
        self.vagtperioder_listbox.selection_set(0)

    def on_select_period(self, event):
        w = event.widget
        if len(w.curselection()) == 0:
            return
        index = int(w.curselection()[0])
        self.selected_index = index
        self.sync_form()

    def sync_list(self):
        self.vagtperioder_var.set(
            [vagtperiode.to_string() for vagtperiode in self.vagtperioder]
        )
        self.vagtperioder_listbox.select_clear(0, tk.END)
        self.vagtperioder_listbox.selection_set(self.selected_index)

        for i in range(0, len(self.vagtperioder_var.get()), 2):
            self.vagtperioder_listbox.itemconfigure(i, background="#f0f0ff")

    def sync_form(self):
        self.startdate_var.set(
            self.vagtperioder[self.selected_index].start.strftime("%Y-%m-%d %H:%M")
        )
        self.enddate_var.set(
            self.vagtperioder[self.selected_index].end.strftime("%Y-%m-%d %H:%M")
        )
        self.vagttørn_entry.current(
            self.vagtperioder[self.selected_index].starting_shift - 1
        )
        self.vagtperiode_type.set(self.vagtperioder[self.selected_index].vagttype)
        self.note_var.set(self.vagtperioder[self.selected_index].note)

    def save_action(self):
        self.vagtperioder[self.selected_index].vagttype = self.vagtperiode_type.get()
        self.vagtperioder[self.selected_index].start = datetime.fromisoformat(
            self.startdate_var.get()
        )
        self.vagtperioder[self.selected_index].end = datetime.fromisoformat(
            self.enddate_var.get()
        )
        self.vagtperioder[self.selected_index].starting_shift = (
            self.vagttørn_entry["values"].index(self.vagttørn_entry.get()) + 1
        )
        self.vagtperioder[self.selected_index].note = self.note_var.get()
        self.sync_list()
        self.on_save()
        # print(json.dumps(self.vagtperioder, cls=EnhancedJSONEncoder, ensure_ascii=False))

    def add_item(self):
        self.vagtperioder.append(
            VagtPeriode(
                "Søvagt",
                datetime.fromisoformat("2024-12-02 10:00"),
                datetime.fromisoformat("2024-12-06 14:00"),
                "Korsør-Helsinki",
                2,
            )
        )
        self.selected_index = len(self.vagtperioder) - 1
        self.sync_form()
        self.sync_list()

    def remove_item(self):
        del self.vagtperioder[self.selected_index]
        if self.selected_index >= len(self.vagtperioder) - 1:
            self.selected_index = len(self.vagtperioder) - 1
        self.sync_form()
        self.sync_list()
