import logging
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

from dateutil.parser import parse

from georgstage.model import Opgave

logger = logging.getLogger()

NO_DATE = "-"

LABELS = {
    Opgave.VAGTHAVENDE_ELEV: "Vagthavende elev",
    Opgave.ORDONNANS: "Ordonnans",
    Opgave.UDKIG: "Udkig",
    Opgave.BJAERGEMAERS: "Bjærgemærs",
    Opgave.RORGAENGER: "Rorgænger",
    Opgave.UDSAETNINGSGAST_A: "Udsætningsgast A",
    Opgave.UDSAETNINGSGAST_B: "Udsætningsgast B",
    Opgave.UDSAETNINGSGAST_C: "Udsætningsgast C",
    Opgave.UDSAETNINGSGAST_D: "Udsætningsgast D",
    Opgave.UDSAETNINGSGAST_E: "Udsætningsgast E",
    Opgave.PEJLEGAST_A: "Pejlegast A",
    Opgave.PEJLEGAST_B: "Pejlegast B",
    Opgave.DAEKSELEV_I_KABYS: "Dækselev i kabys",
    Opgave.HU: "HU",
    Opgave.UDE: "Ude (hele dagen)",
}


class View(tk.Tk):
    """docstring for View."""

    PAD = 30
    WIDTH = 12
    ROWS = 12
    COLS = 6

    def __init__(self, controller, model):
        super(View, self).__init__()
        self.controller = controller
        self.model = model
        self.title("Georg Stage vagtplanlægger")
        self.configure(bg="#048A81")
        # Register validator

        def is_gast_or_empty(str):
            return str == "" or (str.isdigit() and 0 < int(str) <= 60)

        self.vcmd = (self.register(is_gast_or_empty), "%P")
        # Create UI
        self._make_gui()
        self.update()

    def main(self):
        logger.debug("In main of view ")
        self.mainloop()

    def _make_gui(self):
        # Make vars
        self._vars = {}
        self.current_date = tk.StringVar(self)
        self.current_date.set(NO_DATE)
        self.current_date.trace("w", self._on_date_selected)
        self.hint = tk.StringVar(self)

        # Make mainframe
        self.main_frm = tk.Frame(self, bg="White")
        self.main_frm.pack(padx=self.PAD, pady=self.PAD, side=tk.TOP)

        # Make menu
        menu = tk.Menu(self)
        self.config(menu=menu)
        file_menu = tk.Menu(menu)
        menu.add_cascade(label="Filer", menu=file_menu)
        file_menu.add_command(label="Åben vagtplan", command=self.controller.open_file)
        file_menu.add_command(
            label="Gem vagtplan", command=self.controller.save_file_as
        )
        file_menu.add_command(
            label="Eksporter til word", command=self.controller.export_word
        )
        rediger_menu = tk.Menu(menu)
        menu.add_cascade(label="Rediger", menu=rediger_menu)
        rediger_menu.add_command(
            label="Opret ny dato", command=self.controller.create_date
        )
        rediger_menu.add_command(label="Ryd vagter", command=self.controller.reset_date)
        rediger_menu.add_command(label="Slet dato", command=self.controller.delete_date)
        function_menu = tk.Menu(menu)
        menu.add_cascade(label="Funktioner", menu=function_menu)
        function_menu.add_command(
            label="Udfyld resten automatisk", command=self.controller.autofill
        )
        function_menu.add_command(
            label="Vis statistik", command=self.controller.show_stats
        )
        help_menu = tk.Menu(menu)
        menu.add_cascade(label="Hjælp", menu=help_menu)
        help_menu.add_command(
            label="Om Georg Stage vagtplanlægger", command=self.controller.get_help
        )

        # Make labels
        # Hint
        tk.Label(self.main_frm, bg="White", textvariable=self.hint, fg="red").grid(
            row=0, column=1, columnspan=5, sticky=tk.W
        )
        # Spacer
        tk.Label(self.main_frm, bg="White", text="").grid(row=1, column=0, sticky=tk.E)
        # Opgave labels
        tk.Label(self.main_frm, bg="White", text=LABELS[Opgave.VAGTHAVENDE_ELEV]).grid(
            row=2, column=0, sticky=tk.E
        )
        tk.Label(self.main_frm, bg="White", text=LABELS[Opgave.ORDONNANS]).grid(
            row=3, column=0, sticky=tk.E
        )
        tk.Label(self.main_frm, bg="White", text=LABELS[Opgave.UDKIG]).grid(
            row=4, column=0, sticky=tk.E
        )
        tk.Label(self.main_frm, bg="White", text=LABELS[Opgave.BJAERGEMAERS]).grid(
            row=5, column=0, sticky=tk.E
        )
        tk.Label(self.main_frm, bg="White", text=LABELS[Opgave.RORGAENGER]).grid(
            row=6, column=0, sticky=tk.E
        )
        tk.Label(self.main_frm, bg="White", text=LABELS[Opgave.UDSAETNINGSGAST_A]).grid(
            row=7, column=0, sticky=tk.E
        )
        tk.Label(self.main_frm, bg="White", text=LABELS[Opgave.UDSAETNINGSGAST_B]).grid(
            row=8, column=0, sticky=tk.E
        )
        tk.Label(self.main_frm, bg="White", text=LABELS[Opgave.UDSAETNINGSGAST_C]).grid(
            row=9, column=0, sticky=tk.E
        )
        tk.Label(self.main_frm, bg="White", text=LABELS[Opgave.UDSAETNINGSGAST_D]).grid(
            row=10, column=0, sticky=tk.E
        )
        tk.Label(self.main_frm, bg="White", text=LABELS[Opgave.UDSAETNINGSGAST_E]).grid(
            row=11, column=0, sticky=tk.E
        )
        tk.Label(self.main_frm, bg="White", text="Pejlegast A/B").grid(
            row=12, column=0, sticky=tk.E
        )
        tk.Label(self.main_frm, bg="White", text=LABELS[Opgave.DAEKSELEV_I_KABYS]).grid(
            row=13, column=0, sticky=tk.E
        )
        # Tidspunkt labels
        tk.Label(self.main_frm, bg="White", text="08 - 12", width=self.WIDTH).grid(
            row=1, column=1, sticky=tk.E
        )
        tk.Label(self.main_frm, bg="White", text="12 - 16", width=self.WIDTH).grid(
            row=1, column=2, sticky=tk.E
        )
        tk.Label(self.main_frm, bg="White", text="16 - 20", width=self.WIDTH).grid(
            row=1, column=3, sticky=tk.E
        )
        tk.Label(self.main_frm, bg="White", text="20 - 24", width=self.WIDTH).grid(
            row=1, column=4, sticky=tk.E
        )
        tk.Label(self.main_frm, bg="White", text="00 - 04", width=self.WIDTH).grid(
            row=1, column=5, sticky=tk.E
        )
        tk.Label(self.main_frm, bg="White", text="04 - 08", width=self.WIDTH).grid(
            row=1, column=6, sticky=tk.E
        )
        # Spacer
        tk.Label(self.main_frm, bg="White", text="").grid(row=14, column=0, sticky=tk.E)
        # HU
        tk.Label(self.main_frm, bg="White", text=LABELS[Opgave.HU]).grid(
            row=15, column=0, sticky=tk.E
        )
        # Spacer
        tk.Label(self.main_frm, bg="White", text="").grid(row=16, column=0, sticky=tk.E)
        # Ude
        tk.Label(self.main_frm, bg="White", text=LABELS[Opgave.UDE]).grid(
            row=17, column=0, sticky=tk.E
        )

        # Make dropdown
        date_list = [NO_DATE]
        self.current_date.set(date_list[0])
        self._dropdown = tk.OptionMenu(self.main_frm, self.current_date, *date_list)
        self._dropdown.grid(row=0, column=0, sticky=tk.E)

        # Make fields
        # Vagthavende elev
        self._make_entry(opgave=Opgave.VAGTHAVENDE_ELEV, tid=8, row=2, col=1)
        self._make_entry(opgave=Opgave.VAGTHAVENDE_ELEV, tid=12, row=2, col=2)
        self._make_entry(opgave=Opgave.VAGTHAVENDE_ELEV, tid=16, row=2, col=3)
        self._make_entry(opgave=Opgave.VAGTHAVENDE_ELEV, tid=20, row=2, col=4)
        self._make_entry(opgave=Opgave.VAGTHAVENDE_ELEV, tid=0, row=2, col=5)
        self._make_entry(opgave=Opgave.VAGTHAVENDE_ELEV, tid=4, row=2, col=6)

        # Ordonnans
        self._make_entry(opgave=Opgave.ORDONNANS, tid=8, row=3, col=1)
        self._make_entry(opgave=Opgave.ORDONNANS, tid=12, row=3, col=2)
        self._make_entry(opgave=Opgave.ORDONNANS, tid=16, row=3, col=3)
        self._make_entry(opgave=Opgave.ORDONNANS, tid=20, row=3, col=4)
        self._make_entry(opgave=Opgave.ORDONNANS, tid=0, row=3, col=5)
        self._make_entry(opgave=Opgave.ORDONNANS, tid=4, row=3, col=6)

        # Udkig
        self._make_entry(opgave=Opgave.UDKIG, tid=8, row=4, col=1)
        self._make_entry(opgave=Opgave.UDKIG, tid=12, row=4, col=2)
        self._make_entry(opgave=Opgave.UDKIG, tid=16, row=4, col=3)
        self._make_entry(opgave=Opgave.UDKIG, tid=20, row=4, col=4)
        self._make_entry(opgave=Opgave.UDKIG, tid=0, row=4, col=5)
        self._make_entry(opgave=Opgave.UDKIG, tid=4, row=4, col=6)

        # Bjaergemaers
        self._make_entry(opgave=Opgave.BJAERGEMAERS, tid=8, row=5, col=1)
        self._make_entry(opgave=Opgave.BJAERGEMAERS, tid=12, row=5, col=2)
        self._make_entry(opgave=Opgave.BJAERGEMAERS, tid=16, row=5, col=3)
        self._make_entry(opgave=Opgave.BJAERGEMAERS, tid=20, row=5, col=4)
        self._make_entry(opgave=Opgave.BJAERGEMAERS, tid=0, row=5, col=5)
        self._make_entry(opgave=Opgave.BJAERGEMAERS, tid=4, row=5, col=6)

        # Rorganger
        self._make_entry(opgave=Opgave.RORGAENGER, tid=8, row=6, col=1)
        self._make_entry(opgave=Opgave.RORGAENGER, tid=12, row=6, col=2)
        self._make_entry(opgave=Opgave.RORGAENGER, tid=16, row=6, col=3)
        self._make_entry(opgave=Opgave.RORGAENGER, tid=20, row=6, col=4)
        self._make_entry(opgave=Opgave.RORGAENGER, tid=0, row=6, col=5)
        self._make_entry(opgave=Opgave.RORGAENGER, tid=4, row=6, col=6)

        # Udsaetningsgast A
        self._make_entry(opgave=Opgave.UDSAETNINGSGAST_A, tid=8, row=7, col=1)
        self._make_entry(opgave=Opgave.UDSAETNINGSGAST_A, tid=12, row=7, col=2)
        self._make_entry(opgave=Opgave.UDSAETNINGSGAST_A, tid=16, row=7, col=3)
        self._make_entry(opgave=Opgave.UDSAETNINGSGAST_A, tid=20, row=7, col=4)
        self._make_entry(opgave=Opgave.UDSAETNINGSGAST_A, tid=0, row=7, col=5)
        self._make_entry(opgave=Opgave.UDSAETNINGSGAST_A, tid=4, row=7, col=6)

        # Udsaetningsgast B
        self._make_entry(opgave=Opgave.UDSAETNINGSGAST_B, tid=8, row=8, col=1)
        self._make_entry(opgave=Opgave.UDSAETNINGSGAST_B, tid=12, row=8, col=2)
        self._make_entry(opgave=Opgave.UDSAETNINGSGAST_B, tid=16, row=8, col=3)
        self._make_entry(opgave=Opgave.UDSAETNINGSGAST_B, tid=20, row=8, col=4)
        self._make_entry(opgave=Opgave.UDSAETNINGSGAST_B, tid=0, row=8, col=5)
        self._make_entry(opgave=Opgave.UDSAETNINGSGAST_B, tid=4, row=8, col=6)

        # Udsaetningsgast C
        self._make_entry(opgave=Opgave.UDSAETNINGSGAST_C, tid=8, row=9, col=1)
        self._make_entry(opgave=Opgave.UDSAETNINGSGAST_C, tid=12, row=9, col=2)
        self._make_entry(opgave=Opgave.UDSAETNINGSGAST_C, tid=16, row=9, col=3)
        self._make_entry(opgave=Opgave.UDSAETNINGSGAST_C, tid=20, row=9, col=4)
        self._make_entry(opgave=Opgave.UDSAETNINGSGAST_C, tid=0, row=9, col=5)
        self._make_entry(opgave=Opgave.UDSAETNINGSGAST_C, tid=4, row=9, col=6)

        # Udsaetningsgast D
        self._make_entry(opgave=Opgave.UDSAETNINGSGAST_D, tid=8, row=10, col=1)
        self._make_entry(opgave=Opgave.UDSAETNINGSGAST_D, tid=12, row=10, col=2)
        self._make_entry(opgave=Opgave.UDSAETNINGSGAST_D, tid=16, row=10, col=3)
        self._make_entry(opgave=Opgave.UDSAETNINGSGAST_D, tid=20, row=10, col=4)
        self._make_entry(opgave=Opgave.UDSAETNINGSGAST_D, tid=0, row=10, col=5)
        self._make_entry(opgave=Opgave.UDSAETNINGSGAST_D, tid=4, row=10, col=6)

        # Udsaetningsgast E
        self._make_entry(opgave=Opgave.UDSAETNINGSGAST_E, tid=8, row=11, col=1)
        self._make_entry(opgave=Opgave.UDSAETNINGSGAST_E, tid=12, row=11, col=2)
        self._make_entry(opgave=Opgave.UDSAETNINGSGAST_E, tid=16, row=11, col=3)
        self._make_entry(opgave=Opgave.UDSAETNINGSGAST_E, tid=20, row=11, col=4)
        self._make_entry(opgave=Opgave.UDSAETNINGSGAST_E, tid=0, row=11, col=5)
        self._make_entry(opgave=Opgave.UDSAETNINGSGAST_E, tid=4, row=11, col=6)

        # Pejlegaster
        pejlegast_frame = tk.Frame(self.main_frm)
        var_pejlegast_a = self._vars.setdefault(
            (Opgave.PEJLEGAST_A, 16), tk.StringVar(self)
        )
        var_pejlegast_b = self._vars.setdefault(
            (Opgave.PEJLEGAST_B, 16), tk.StringVar(self)
        )
        tk.Entry(
            pejlegast_frame,
            validate="key",
            validatecommand=self.vcmd,
            textvariable=var_pejlegast_a,
            justify="right",
            width=4,
        ).pack(side=tk.LEFT)
        tk.Entry(
            pejlegast_frame,
            validate="key",
            validatecommand=self.vcmd,
            textvariable=var_pejlegast_b,
            justify="right",
            width=4,
        ).pack(side=tk.LEFT)
        pejlegast_frame.grid(row=12, column=3)

        # Daekselev i kabys
        self._make_entry(opgave=Opgave.DAEKSELEV_I_KABYS, tid=8, row=13, col=1)
        self._make_entry(opgave=Opgave.DAEKSELEV_I_KABYS, tid=12, row=13, col=2)
        self._make_entry(opgave=Opgave.DAEKSELEV_I_KABYS, tid=16, row=13, col=3)
        self._make_entry(opgave=Opgave.DAEKSELEV_I_KABYS, tid=4, row=13, col=6)

        # Ude/HU
        # 8-12
        self._make_list_entry(opgave=Opgave.HU, tid=8, row=15, col=1)
        # 12-16
        self._make_list_entry(opgave=Opgave.HU, tid=12, row=15, col=2)
        # 16-20
        self._make_list_entry(opgave=Opgave.HU, tid=16, row=15, col=3)
        # 20-24
        self._make_list_entry(opgave=Opgave.HU, tid=20, row=15, col=4)
        # 00-04
        self._make_list_entry(opgave=Opgave.HU, tid=0, row=15, col=5)
        # 04-08
        self._make_list_entry(opgave=Opgave.HU, tid=4, row=15, col=6)

        # Ude
        self._make_list_entry(opgave=Opgave.UDE, tid=-1, row=17, col=1, colspan=2)

    def _refresh_datoer(self, datoer):
        date_list = sorted([d.isoformat() for d in datoer])
        self._dropdown["menu"].delete(0, "end")
        for dato in date_list:
            self._dropdown["menu"].add_command(
                label=dato, command=tk._setit(self.current_date, dato)
            )

    def _refresh_vagter(self, vagter):
        # ugly, ugly HU handling
        multi_vagter = {}
        for vagt in vagter:
            key = (vagt.opgave, vagt.vagt_tid)
            if vagt.opgave in {Opgave.HU, Opgave.UDE}:
                multi_vagter.setdefault(key, []).append(str(vagt.gast))
            else:
                text = str(vagt.gast)
                self._vars[key].set(text)
        for key, gaster in multi_vagter.items():
            text = ", ".join(sorted(gaster))
            self._vars[key].set(text)

    def update(self):
        logger.debug("Updating")
        # get model state
        dt = self.model.get_current_dato()
        datoer = self.model.get_datoer()
        if dt is None:
            self.hint.set(
                "Vælg Filer > Åben vagtplan eller Rediger > Opret dato for at fortsætte"
            )
            vagter = []
        else:
            self.hint.set("")
            vagter = self.model[dt]
        # redraw UI
        self._clear_screen()
        self._refresh_datoer(datoer)
        self._refresh_vagter(vagter)
        # set correct date. Stinks a bit. Necessary?
        display_date = dt.isoformat() if dt is not None else NO_DATE
        self.current_date.set(display_date)

    def set_model(self, model):
        self.model = model

    def _get_vars_helper(self):
        for k, v in self._vars.items():
            text = v.get().strip()
            if k[0] in {Opgave.UDE, Opgave.HU}:
                for sub_text in sorted(text.split(",")):
                    yield k, sub_text.strip()
            else:
                yield k, text

    def get_vars(self):
        return list(self._get_vars_helper())

    def get_current_date(self):
        return self.current_date.get()

    def _clear_screen(self):
        logger.debug("Resetting variables")
        for var in self._vars.values():
            var.set("")

    def _make_entry(self, opgave, tid, row, col):
        key = (opgave, tid)
        var = self._vars.setdefault(key, tk.StringVar(self))
        return tk.Entry(
            self.main_frm,
            validate="key",
            validatecommand=self.vcmd,
            justify="right",
            textvariable=var,
            width=self.WIDTH,
        ).grid(row=row, column=col, sticky=tk.W)

    def _make_list_entry(self, opgave, tid, row, col, colspan=1, sticky=tk.W):
        key = (opgave, tid)
        var = self._vars.setdefault(key, tk.StringVar(self))
        return tk.Entry(
            self.main_frm, justify="right", textvariable=var, width=self.WIDTH * colspan
        ).grid(row=row, column=col, columnspan=colspan, sticky=sticky)

    def show_info(self, header, text):
        messagebox.showinfo(header, text, parent=self.main_frm)

    def show_warning(self, title, message):
        messagebox.showwarning(title, message, parent=self.main_frm)

    def ask_open_file(self, **kwargs):
        return filedialog.askopenfilename(**kwargs, parent=self.main_frm)

    def ask_save_file_as(self, **kwargs):
        return filedialog.asksaveasfilename(**kwargs, parent=self.main_frm)

    def ask_number(self, header, text):
        number = simpledialog.askinteger(header, text, parent=self.main_frm)
        return number

    def ask_string(self, title, prompt, initial_value):
        str = simpledialog.askstring(
            title, prompt, initialvalue=initial_value, parent=self.main_frm
        )
        return str

    def ask_consent(self, header, text):
        return messagebox.askokcancel(header, text, parent=self.main_frm)

    def show_table(self, rows, columns_labels, row_labels, header="Tabel"):
        # Pop-up window.
        table_window = tk.Toplevel()
        table_window.title(header)
        # Frame
        frame = tk.Frame(table_window, bg="White")
        frame.pack(padx=self.PAD, pady=self.PAD, side=tk.TOP)
        for i, label in enumerate(columns_labels):
            tk.Label(frame, bg="White", text=label).grid(
                row=0, column=i + 1, sticky=tk.E
            )
        for i, label in enumerate(row_labels):
            tk.Label(frame, bg="White", text=label).grid(
                row=i + 1, column=0, sticky=tk.E
            )
        for i, row in enumerate(rows):
            for j, item in enumerate(row):
                tk.Label(frame, bg="White", text=str(item)).grid(
                    row=i + 1, column=j + 1, sticky=tk.E
                )

    def _on_date_selected(self, a, b, c):
        if self.current_date.get() == NO_DATE:
            return
        new_date = parse(self.current_date.get()).date()
        self.controller.change_date(new_date)
