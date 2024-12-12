import tkinter as tk
from tkinter import ttk

from georgstage.components.vertical_scroll import VerticalScrolledFrame
from georgstage.util import make_cell
from georgstage.registry import Registry
from georgstage.model import Opgave, VagtSkifte
from georgstage.solver import count_vagt_stats, kabys_elev_nrs, get_skifte_from_elev_nr

from enum import Enum

class VagtKategori(Enum):
    VAGTHAVENDE = 'Vagthavende ELEV'
    FYSISK_VAGT = 'Fysisk vagt'
    KABYS = 'Dækselev i kabys'
    PEJLEGAST = 'Pejlegast'

vagt_kategori_associations = {
    VagtKategori.VAGTHAVENDE: [
        Opgave.VAGTHAVENDE_ELEV,
    ],
    VagtKategori.FYSISK_VAGT: [
        Opgave.ORDONNANS,
        Opgave.UDKIG,
        Opgave.RADIOVAGT,
        Opgave.RORGAENGER,
    ],
    VagtKategori.KABYS: [
        Opgave.DAEKSELEV_I_KABYS,
    ],
    VagtKategori.PEJLEGAST: [
        Opgave.PEJLEGAST_A,
        Opgave.PEJLEGAST_B,
    ],
}

skifte_labels = {
    VagtSkifte.SKIFTE_1: 'Første skifte',
    VagtSkifte.SKIFTE_2: 'Andet skifte',
    VagtSkifte.SKIFTE_3: 'Tredje skifte',
}

class StatistikTab(ttk.Frame):
    def __init__(self, parent, registry: Registry, *args, **kwargs) -> None:
        ttk.Frame.__init__(self, parent, padding=(5, 5, 12, 0), *args, **kwargs)
        self.bind('<Visibility>', lambda _: table_frame.interior.focus_force())
        self.registry = registry
        self.registry.register_update_listener(self.on_registry_change)


        # State variables
        self.stats_table_vars: dict[tuple[VagtKategori, int], tk.StringVar] = {}

        # GUI Elements
        table_frame = VerticalScrolledFrame(self)
        v_sep = ttk.Separator(self, orient=tk.VERTICAL)
        self.stats_frame = ttk.Frame(self)
        
        # Create label row
        for col, label in enumerate(VagtKategori.__members__.values()):
            make_cell(
                table_frame.interior,
                0,
                col + 1,
                label.value,
                14,
                False,
            )

        # Create numbers column in col 0
        make_cell(table_frame.interior,0,0,'',5,False)
        for row in range(1,64):
            if row in kabys_elev_nrs:
                continue
            make_cell(
                table_frame.interior,
                row + 1,
                0,
                str(row),
                5,
                False,
            )
        
        # Create empty cells with variables
        for row in range(1,64):
            if row in kabys_elev_nrs:
                continue
            for col, label in enumerate(VagtKategori.__members__.values()):
                self.stats_table_vars[(label, row)] = tk.StringVar()
                make_cell(
                    table_frame.interior,
                    row + 1,
                    col + 1,
                    '',
                    14,
                    False,
                    self.stats_table_vars[(label, row)],
                )

        table_frame.grid(column=2, row=0, sticky='nsw', pady=(0,5))
        v_sep.grid(column=1, row=0, sticky='ns', padx=10, pady=(0,5))
        self.stats_frame.grid(column=0, row=0, pady=(0,5), sticky='nsew')

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.on_registry_change()

    def on_registry_change(self) -> None:
        stats: dict[tuple[Opgave, int], int] = count_vagt_stats(self.registry.vagtlister)
        summed_stats: dict[tuple[VagtKategori, int], int] = {}
        summed_stats_skifte: dict[tuple[VagtKategori, int], int] = {}

        for (opgave, elev_nr), count in stats.items():
            for kategori, opgaver in vagt_kategori_associations.items():
                if opgave in opgaver:
                    summed_stats[(kategori, elev_nr)] = summed_stats.get((kategori, elev_nr), 0) + count
                    summed_stats_skifte[(kategori, get_skifte_from_elev_nr(elev_nr))] = summed_stats_skifte.get((kategori, get_skifte_from_elev_nr(elev_nr)), 0) + count

        for (kategori, elev_nr), count in summed_stats.items():
            self.stats_table_vars[(kategori, elev_nr)].set(str(count))

        for child in self.stats_frame.winfo_children():
            child.destroy()
        
        title = ttk.Label(self.stats_frame, text="Vagtstatistik", font=("Calibri", 16, "bold"))
        title.pack()

        for skifte in VagtSkifte.__members__.values():
            ttk.Label(self.stats_frame , text=f"{skifte_labels[skifte]}:").pack(anchor='nw',side='top', pady=(10, 0))
            for kategori in VagtKategori:
                ttk.Label(self.stats_frame , text=f" - {kategori.value}: {summed_stats_skifte.get((kategori, skifte), 0)}").pack(anchor='nw',side='top')