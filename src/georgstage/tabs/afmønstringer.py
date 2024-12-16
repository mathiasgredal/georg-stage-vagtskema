from tkinter import ttk
import tkinter as tk
from georgstage.registry import Registry
from georgstage.model import Afmønstring, VagtTid, Opgave
from georgstage.solver import autofill_vagtliste
from uuid import uuid4, UUID
from datetime import date, timedelta


class AfmønstringTab(ttk.Frame):
    def __init__(self, parent, registry: Registry, *args, **kwargs) -> None:
        ttk.Frame.__init__(self, parent, padding=(5, 5, 12, 0), *args, **kwargs)
        self.registry = registry
        self.registry.register_update_listener(self.on_update)

        self.selected_afmønstring_id: UUID | None = None
        self.can_update_vls = False

        # State variables
        self.afmønstring_list_var = tk.Variable()
        self.elev_nr_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.start_date_var = tk.StringVar()
        self.end_date_var = tk.StringVar()

        # GUI Elements
        self.afmønstring_listbox = tk.Listbox(
            self, listvariable=self.afmønstring_list_var, height=15, selectmode=tk.SINGLE, exportselection=False
        )
        self.afmønstring_listbox.bind('<<ListboxSelect>>', self.on_select)
        self.afmønstring_sep = ttk.Separator(self, orient=tk.VERTICAL)
        self.afmønstring_detail = ttk.Frame(self)
        self.afmønstring_form = ttk.Frame(self.afmønstring_detail)
        self.afmønstring_no_selection = ttk.Frame(self.afmønstring_detail)

        self.title = ttk.Label(self.afmønstring_detail, text='Afmønstringer', font=('Calibri', 16, 'bold'))

        self.elev_nr_label = ttk.Label(self.afmønstring_form, text='Elev nr:')
        self.elev_nr_entry = ttk.Entry(self.afmønstring_form, textvariable=self.elev_nr_var)

        self.name_label = ttk.Label(self.afmønstring_form, text='Navn:')
        self.name_entry = ttk.Entry(self.afmønstring_form, textvariable=self.name_var)

        self.start_date_label = ttk.Label(self.afmønstring_form, text='Start dato:')
        self.start_date_entry = ttk.Entry(self.afmønstring_form, textvariable=self.start_date_var)

        self.end_date_label = ttk.Label(self.afmønstring_form, text='Slut dato:')
        self.end_date_entry = ttk.Entry(self.afmønstring_form, textvariable=self.end_date_var)

        self.btn_row = ttk.Frame(self)
        self.add_btn = ttk.Button(self.btn_row, text='Tilføj...', command=self.add_item)
        self.remove_btn = ttk.Button(self.btn_row, text='Fjern', command=self.remove_item)
        self.save_btn = ttk.Button(self.btn_row, text='Gem', default='active', command=self.save_action)
        self.update_vls_btn = ttk.Button(self.btn_row, text='Opdater vagtlister...', command=self.update_vls)

        self.help_label = ttk.Label(
            self.afmønstring_no_selection,
            text='Vælg venligst en afmønstring fra listen\n eller tilføj en ny afmønstring.',
            font='TkDefaultFont 12 italic',
            justify='center',
        )

        # Layout
        self.afmønstring_listbox.grid(column=0, row=0, sticky='nsew', pady=(0, 5))
        self.afmønstring_sep.grid(column=1, row=0, sticky='ns', padx=10, pady=(0, 5))
        self.afmønstring_detail.grid(column=2, row=0, sticky='nsew', pady=(0, 5))
        self.title.grid(column=0, row=0, padx=53)
        self.afmønstring_no_selection.grid(column=0, row=1, sticky='nsew')
        self.afmønstring_form.grid(column=0, row=1, sticky='nsew')

        self.elev_nr_label.pack(anchor='nw', side='top', pady=(10, 0))
        self.elev_nr_entry.pack(anchor='nw', side='top', padx=10)
        self.name_label.pack(anchor='nw', side='top', pady=(10, 0))
        self.name_entry.pack(anchor='nw', side='top', padx=10)
        self.start_date_label.pack(anchor='nw', side='top', pady=(10, 0))
        self.start_date_entry.pack(anchor='nw', side='top', padx=10)
        self.end_date_label.pack(anchor='nw', side='top', pady=(10, 0))
        self.end_date_entry.pack(anchor='nw', side='top', padx=10)

        self.help_label.pack(anchor='n', side='top', pady=10)

        self.btn_row.grid(column=0, row=2, columnspan=3, sticky='nsew', pady=(0, 10))
        self.add_btn.pack(side='left', padx=(0, 10))
        self.remove_btn.pack(side='left')
        self.save_btn.pack(side='right')

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sync_list()
        self.sync_form()

    def on_select(self, event: tk.Event) -> None:  # type: ignore
        w = event.widget
        if len(w.curselection()) == 0:
            return
        index = int(w.curselection()[0])
        self.selected_afmønstring_id = self.registry.afmønstringer[index].id
        self.sync_form()

    def sync_list(self) -> None:
        """Sync the listbox with the registry"""
        self.afmønstring_list_var.set([afmønstring.to_string() for afmønstring in self.registry.afmønstringer])
        self.afmønstring_listbox.select_clear(0, tk.END)
        selected_index = self._get_afmønstring_index(self.selected_afmønstring_id)
        if selected_index is not None:
            self.afmønstring_listbox.selection_set(selected_index)
        for i in range(0, len(self.afmønstring_list_var.get()), 2):  # type: ignore
            self.afmønstring_listbox.itemconfigure(i, background='#f0f0ff')

    def sync_form(self) -> None:
        """Sync the form with the selected item"""
        if self.selected_afmønstring_id is None:
            self.afmønstring_no_selection.tkraise()
            return
        self.afmønstring_form.tkraise()

        selected_afmønstring = self.registry.get_afmønstring_by_id(self.selected_afmønstring_id)
        if selected_afmønstring is None:
            return

        self.elev_nr_var.set(selected_afmønstring.elev_nr)
        self.name_var.set(selected_afmønstring.name)
        self.start_date_var.set(selected_afmønstring.start_date.strftime('%Y-%m-%d'))
        self.end_date_var.set(selected_afmønstring.end_date.strftime('%Y-%m-%d'))

        # Check if there are any vagter with the given elev nr in the date interval
        for vagtliste in self.registry.vagtlister:
            for _, vagt in vagtliste.vagter.items():
                for _, nr in vagt.opgaver.items():
                    for afmønstring in self.registry.afmønstringer:
                        if (
                            nr == afmønstring.elev_nr
                            and afmønstring.start_date <= vagtliste.start.date()
                            and vagtliste.end.date() <= afmønstring.end_date
                        ):
                            self.can_update_vls = True
                            break

        if self.can_update_vls:
            self.update_vls_btn.pack(side='right', padx=(0, 10))
            self.update_vls_btn.focus_force()

    def save_action(self) -> None:
        """Save the form data into the registry"""
        if self.selected_afmønstring_id is None:
            return
        selected_afmønstring = self.registry.get_afmønstring_by_id(self.selected_afmønstring_id)
        if selected_afmønstring is None:
            return
        selected_afmønstring.elev_nr = int(self.elev_nr_var.get())
        selected_afmønstring.name = self.name_var.get()
        selected_afmønstring.start_date = date.fromisoformat(self.start_date_var.get())
        selected_afmønstring.end_date = date.fromisoformat(self.end_date_var.get())
        self.sync_list()
        self.sync_form()

    def add_item(self) -> None:
        self.registry.afmønstringer.append(
            Afmønstring(
                id=uuid4(),
                elev_nr=0,
                name='John Doe',
                start_date=date.today(),
                end_date=date.today() + timedelta(days=1),
            )
        )
        self.selected_afmønstring_id = self.registry.afmønstringer[-1].id
        self.sync_list()
        self.sync_form()

    def remove_item(self) -> None:
        if self.selected_afmønstring_id is None:
            return
        index = self._get_afmønstring_index(self.selected_afmønstring_id)
        if index is not None:
            del self.registry.afmønstringer[index]
        self.selected_afmønstring_id = (
            self.registry.afmønstringer[-1].id if len(self.registry.afmønstringer) > 0 else None
        )
        self.sync_list()
        self.sync_form()

    def update_vls(self) -> None:
        # Remove all opgaver with the given elev nr in the date interval
        for afmønstring in self.registry.afmønstringer:
            for vagtliste in self.registry.vagtlister:
                if not (
                    afmønstring.start_date <= vagtliste.start.date() and vagtliste.end.date() <= afmønstring.end_date
                ):
                    continue

                to_remove: list[tuple[VagtTid, Opgave]] = []
                for tid, vagt in vagtliste.vagter.items():
                    for opg, nr in vagt.opgaver.items():
                        if nr != afmønstring.elev_nr:
                            continue
                        to_remove.append((tid, opg))

                for tid, opg in to_remove:
                    del vagtliste.vagter[tid].opgaver[opg]

                autofill_vagtliste(vagtliste, self.registry)
        self.registry.notify_update_listeners()
        self.can_update_vls = False
        self.update_vls_btn.pack_forget()

    def on_update(self) -> None:
        self.sync_list()
        self.sync_form()

    def _get_afmønstring_index(self, id: UUID) -> int | None:
        for i, afmønstring in enumerate(self.registry.afmønstringer):
            if afmønstring.id == id:
                return i
        return None
