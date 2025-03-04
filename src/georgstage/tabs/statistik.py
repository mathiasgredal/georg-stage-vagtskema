"""Tab for statistik"""

import tkinter as tk
from tkinter import ttk
from typing import Any

from georgstage.components.fancy_table import FancyTable, HeaderLabel
from georgstage.components.responsive_notebook import ResponsiveNotebook
from georgstage.model import Opgave, VagtSkifte, VagtTid, VagtType, kabys_elev_nrs
from georgstage.registry import Registry
from georgstage.solver import get_skifte_from_elev_nr
from georgstage.util import get_default_font_size

skifte_labels = {
    VagtSkifte.SKIFTE_1: 'Første skifte',
    VagtSkifte.SKIFTE_2: 'Andet skifte',
    VagtSkifte.SKIFTE_3: 'Tredje skifte',
}


class StatistikTab(ttk.Frame):
    """Tab for statistik"""

    def __init__(self, parent: tk.Misc, registry: Registry, *args: Any, **kwargs: Any) -> None:
        ttk.Frame.__init__(self, parent, padding=(5, 5, 12, 0), *args, **kwargs)  # noqa: B026
        self.registry = registry
        self.registry.register_update_listener(self.on_registry_change)

        # State
        self.text_vars: dict[tuple[str, VagtSkifte], tk.StringVar] = {}
        self.vagthavende_elev_vars: dict[tuple[str, int], tk.StringVar] = {}
        self.kabys_vars: dict[tuple[str, int], tk.StringVar] = {}
        self.landgangsvagt_vars: dict[tuple[str, int], tk.StringVar] = {}
        self.holmen_vars: dict[tuple[str, int], tk.StringVar] = {}
        self.others_vars: dict[tuple[str, int], tk.StringVar] = {}

        # GUI Elements
        self.stats_frame = self.make_text_stats(self)
        self.v_sep = ttk.Separator(self, orient=tk.VERTICAL)
        self.notebook = ResponsiveNotebook(self)

        self.notebook.add('Vagthavende ELEV', self.make_vagthavende_elev_table(self.notebook.tab_stack))
        self.notebook.add('Dækselev i kabys', self.make_dækselev_i_kabys_table(self.notebook.tab_stack))
        self.notebook.add('Landgangsvagt', self.make_landgangsvagt_table(self.notebook.tab_stack))
        self.notebook.add('Holmen', self.make_holmen_table(self.notebook.tab_stack))
        self.notebook.add('Andet', self.make_others_table(self.notebook.tab_stack))

        # Layout
        self.stats_frame.grid(column=0, row=0, pady=(0, 5), sticky='nsew')
        self.v_sep.grid(column=1, row=0, sticky='ns', padx=10, pady=(0, 5))
        self.notebook.grid(column=2, row=0, sticky='nsew', pady=(0, 5))

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.on_registry_change()

    def make_text_stats(self, parent: ttk.Frame) -> ttk.Frame:
        """Make the text stats"""
        frame = ttk.Frame(parent)
        ttk.Label(frame, text='Vagtstatistik', font=('TkDefaultFont', get_default_font_size() + 3, 'bold')).pack()

        for skifte in VagtSkifte.__members__.values():
            ttk.Label(
                frame,
                text=f'{skifte_labels[skifte]} [{skifte.value}#]:',
                font=('TkDefaultFont', get_default_font_size(), 'bold'),
            ).pack(anchor='nw', side='top', pady=(10, 0))
            for kategori in [
                'Vagthavende ELEV',
                'Dækselev i kabys',
                'Søvagt',
                'Landgang (Havn)',
                'Pejlegast',
                'HU',
            ]:
                self.text_vars[(kategori, skifte)] = tk.StringVar()
                ttk.Label(frame, textvariable=self.text_vars[(kategori, skifte)]).pack(anchor='nw', side='top')

        return frame

    def make_vagthavende_elev_table(self, parent: ttk.Frame) -> FancyTable:
        """Make the vagthavende elev table"""
        labels: list[HeaderLabel] = [
            HeaderLabel('Søvagt', 13),
            HeaderLabel('Havnevagt', 13),
            HeaderLabel('Holmen', 13),
            HeaderLabel('Samlet', 13),
        ]

        table = FancyTable(
            parent,
            labels,
            self.vagthavende_elev_vars,
            col_0_width=4,
            col_0_ipadx=0,
        )

        return table

    def make_dækselev_i_kabys_table(self, parent: ttk.Frame) -> FancyTable:
        """Make the dækselev i kabys table"""
        labels: list[HeaderLabel] = [
            HeaderLabel('Søvagt', 13),
            HeaderLabel('Havnevagt', 13),
            HeaderLabel('Holmen', 13),
            HeaderLabel('Samlet', 13),
        ]

        table = FancyTable(
            parent,
            labels,
            self.kabys_vars,
            col_0_width=4,
            col_0_ipadx=0,
        )

        return table

    def make_landgangsvagt_table(self, parent: ttk.Frame) -> FancyTable:
        """Make the landgangsvagt table"""
        width = 5
        labels: list[HeaderLabel] = [
            HeaderLabel(VagtTid.T08_12.value, width),
            HeaderLabel(VagtTid.T12_16.value, width),
            HeaderLabel(VagtTid.T16_18.value, width),
            HeaderLabel(VagtTid.T18_20.value, width),
            HeaderLabel(VagtTid.T20_22.value, width),
            HeaderLabel(VagtTid.T22_00.value, width),
            HeaderLabel(VagtTid.T00_02.value, width),
            HeaderLabel(VagtTid.T02_04.value, width),
            HeaderLabel(VagtTid.T04_06.value, width),
            HeaderLabel(VagtTid.T06_08.value, width),
        ]

        table = FancyTable(
            parent,
            labels,
            self.landgangsvagt_vars,
            col_0_width=3,
            col_0_ipadx=2,
        )

        return table

    def make_holmen_table(self, parent: ttk.Frame) -> FancyTable:
        """Make the holmen table"""
        width = 10
        labels: list[HeaderLabel] = [
            HeaderLabel(VagtTid.T22_00.value, width),
            HeaderLabel(VagtTid.T00_02.value, width),
            HeaderLabel(VagtTid.T02_04.value, width),
            HeaderLabel(VagtTid.T04_06.value, width),
            HeaderLabel(VagtTid.T06_08.value, width),
        ]

        table = FancyTable(
            parent,
            labels,
            self.holmen_vars,
            col_0_width=3,
            col_0_ipadx=5,
        )

        return table

    def make_others_table(self, parent: ttk.Frame) -> FancyTable:
        """Make the others table"""
        labels: list[HeaderLabel] = [
            HeaderLabel('HU', 6),
            HeaderLabel('Pejlegast', 9),
            HeaderLabel('Søvagt', 6),
            HeaderLabel('Landgang (Havn)', 14),
            HeaderLabel('Nattevagt (Holmen)', 16),
        ]

        table = FancyTable(
            parent,
            labels,
            self.others_vars,
            col_0_width=4,
            col_0_ipadx=3,
        )

        return table

    def on_registry_change(self) -> None:
        """Update the stats"""
        self.handle_opgave_stats(Opgave.VAGTHAVENDE_ELEV, self.vagthavende_elev_vars)
        self.handle_opgave_stats(Opgave.DAEKSELEV_I_KABYS, self.kabys_vars)
        self.handle_landgangsvagt_stats()
        self.handle_holmen_stats()
        self.handle_others_stats()
        self.handle_text_stats()

    def handle_opgave_stats(self, opgave: Opgave, vars: dict[tuple[str, int], tk.StringVar]) -> None:
        """Handle the opgave stats"""
        stats: dict[tuple[str, int], int] = {}

        for i in range(1, 64):
            if i in kabys_elev_nrs:
                continue

            for label in ['Søvagt', 'Havnevagt', 'Holmen', 'Samlet']:
                stats[(label, i)] = 0

        for vagtliste in self.registry.vagtlister:
            counts: dict[int, int] = {}
            for _, vagt in vagtliste.vagter.items():
                for opg, elev_nr in vagt.opgaver.items():
                    if opg != opgave:
                        continue
                    if elev_nr not in counts:
                        counts[elev_nr] = 0
                    counts[elev_nr] += 1

            for elev_nr, count in counts.items():
                stats[('Samlet', elev_nr)] += count
                if vagtliste.vagttype == VagtType.SOEVAGT:
                    stats[('Søvagt', elev_nr)] += count
                elif vagtliste.vagttype == VagtType.HAVNEVAGT:
                    stats[('Havnevagt', elev_nr)] += count
                elif vagtliste.vagttype in [VagtType.HOLMEN, VagtType.HOLMEN_WEEKEND]:
                    stats[('Holmen', elev_nr)] += count

        for (label, elev_nr), count in stats.items():
            vars[(label, elev_nr)].set(str(count))

    def handle_landgangsvagt_stats(self) -> None:
        """Handle the landgangsvagt stats"""
        stats: dict[tuple[str, int], int] = {}

        for vagtliste in self.registry.vagtlister:
            if vagtliste.vagttype != VagtType.HAVNEVAGT:
                continue

            for tid, vagt in vagtliste.vagter.items():
                for opg, elev_nr in vagt.opgaver.items():
                    if opg not in [Opgave.LANDGANGSVAGT_A, Opgave.LANDGANGSVAGT_B]:
                        continue

                    if (tid.value, elev_nr) not in stats:
                        stats[(tid.value, elev_nr)] = 0

                    stats[(tid.value, elev_nr)] += 1

        for _, var in self.landgangsvagt_vars.items():
            var.set('0')

        for (label, elev_nr), count in stats.items():
            self.landgangsvagt_vars[(label, elev_nr)].set(str(count))

    def handle_holmen_stats(self) -> None:
        """Handle the holmen stats"""
        stats: dict[tuple[str, int], int] = {}

        for vagtliste in self.registry.vagtlister:
            if vagtliste.vagttype not in [VagtType.HOLMEN, VagtType.HOLMEN_WEEKEND]:
                continue

            for tid, vagt in vagtliste.vagter.items():
                for opg, elev_nr in vagt.opgaver.items():
                    if opg not in [Opgave.NATTEVAGT_A, Opgave.NATTEVAGT_B]:
                        continue

                    if (tid.value, elev_nr) not in stats:
                        stats[(tid.value, elev_nr)] = 0

                    stats[(tid.value, elev_nr)] += 1

        for _, var in self.holmen_vars.items():
            var.set('0')

        for (label, elev_nr), count in stats.items():
            self.holmen_vars[(label, elev_nr)].set(str(count))

    def handle_others_stats(self) -> None:
        """Handle the others stats"""
        stats: dict[tuple[str, int], int] = {}

        for vagtliste in self.registry.vagtlister:
            for _, vagt in vagtliste.vagter.items():
                for opg, elev_nr in vagt.opgaver.items():
                    if opg in [Opgave.ORDONNANS, Opgave.UDKIG, Opgave.RADIOVAGT, Opgave.RORGAENGER]:
                        stats[('Søvagt', elev_nr)] = stats.get(('Søvagt', elev_nr), 0) + 1

                    if opg in [Opgave.PEJLEGAST_A, Opgave.PEJLEGAST_B]:
                        stats[('Pejlegast', elev_nr)] = stats.get(('Pejlegast', elev_nr), 0) + 1

                    if opg in [Opgave.LANDGANGSVAGT_A, Opgave.LANDGANGSVAGT_B]:
                        stats[('Landgang (Havn)', elev_nr)] = stats.get(('Landgang (Havn)', elev_nr), 0) + 1

                    if opg in [Opgave.NATTEVAGT_A, Opgave.NATTEVAGT_B]:
                        stats[('Nattevagt (Holmen)', elev_nr)] = stats.get(('Nattevagt (Holmen)', elev_nr), 0) + 1

        # Count HU assignments
        for hu in self.registry.hu:
            should_count = False
            for vagtliste in self.registry.vagtlister:
                if hu.start_date == vagtliste.start.date() and vagtliste.vagttype == VagtType.HAVNEVAGT:
                    should_count = True
                    break

            if not should_count:
                continue

            for assignment in hu.assigned:
                stats[('HU', assignment)] = stats.get(('HU', assignment), 0) + 1

        for _, var in self.others_vars.items():
            var.set('0')

        for (label, elev_nr), count in stats.items():
            if elev_nr == 0:
                continue
            self.others_vars[(label, elev_nr)].set(str(count))

    def handle_text_stats(self) -> None:
        """Handle the text stats"""
        skifte_stats: dict[VagtSkifte, dict[str, int]] = {}

        for i in range(1, 64):
            if i in kabys_elev_nrs:
                continue

            skifte = get_skifte_from_elev_nr(i)

            skifte_stats[skifte] = skifte_stats.get(skifte, {})
            skifte_stats[skifte]['Vagthavende ELEV'] = skifte_stats[skifte].get('Vagthavende ELEV', 0)
            skifte_stats[skifte]['Dækselev i kabys'] = skifte_stats[skifte].get('Dækselev i kabys', 0)
            skifte_stats[skifte]['Søvagt'] = skifte_stats[skifte].get('Søvagt', 0)
            skifte_stats[skifte]['Landgang (Havn)'] = skifte_stats[skifte].get('Landgang (Havn)', 0)
            skifte_stats[skifte]['Pejlegast'] = skifte_stats[skifte].get('Pejlegast', 0)
            skifte_stats[skifte]['HU'] = skifte_stats[skifte].get('HU', 0)

            skifte_stats[skifte]['Vagthavende ELEV'] += self._get_default(self.vagthavende_elev_vars, ('Samlet', i), 0)
            skifte_stats[skifte]['Dækselev i kabys'] += self._get_default(self.kabys_vars, ('Samlet', i), 0)
            skifte_stats[skifte]['Søvagt'] += self._get_default(self.others_vars, ('Søvagt', i), 0)
            skifte_stats[skifte]['Landgang (Havn)'] += self._get_default(self.others_vars, ('Landgang (Havn)', i), 0)
            skifte_stats[skifte]['Pejlegast'] += self._get_default(self.others_vars, ('Pejlegast', i), 0)
            skifte_stats[skifte]['HU'] += self._get_default(self.others_vars, ('HU', i), 0)

        for skifte in VagtSkifte.__members__.values():
            self.text_vars[('Vagthavende ELEV', skifte)].set(
                f' - Vagthavende ELEV: {skifte_stats.get(skifte, {}).get("Vagthavende ELEV", 0)}'
            )
            self.text_vars[('Dækselev i kabys', skifte)].set(
                f' - Dækselev i kabys: {skifte_stats.get(skifte, {}).get("Dækselev i kabys", 0)}'
            )
            self.text_vars[('Søvagt', skifte)].set(f' - Søvagter: {skifte_stats.get(skifte, {}).get("Søvagt", 0)}')
            self.text_vars[('Landgang (Havn)', skifte)].set(
                f' - Landgangsvagter: {skifte_stats.get(skifte, {}).get("Landgang (Havn)", 0)}'
            )
            self.text_vars[('Pejlegast', skifte)].set(
                f' - Pejlegaster: {skifte_stats.get(skifte, {}).get("Pejlegast", 0)}'
            )
            self.text_vars[('HU', skifte)].set(f' - HU: {skifte_stats.get(skifte, {}).get("HU", 0)}')

    def _get_default(self, vars: dict[tuple[str, int], tk.StringVar], key: tuple[str, int], default: int) -> int:
        if key not in vars:
            return default
        return int(vars[key].get())
