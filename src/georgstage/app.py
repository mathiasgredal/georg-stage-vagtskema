import tkinter as tk
from tkinter import ttk
from georgstage.tabs.export import ExportTab
from georgstage.tabs.statistik import StatistikTab
from georgstage.tabs.vagtperioder import VagtPeriodeTab
from georgstage.tabs.vagtliste import VagtListeTab
from georgstage.model import VagtPeriode, VagtListe
from datetime import datetime
from ctypes import windll
import pathlib
# windll.shcore.SetProcessDpiAwareness(½)


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("800x450")
        self.root.title("Georg Stage - Vagtlister")

        self.vagtperioder: list[VagtPeriode] = [
            VagtPeriode(
                "Søvagt",
                datetime.fromisoformat("2024-12-02 13:00"),
                datetime.fromisoformat("2024-12-06 14:00"),
                "Korsør-Helsinki",
                2,
            ),
            VagtPeriode(
                "Havnevagt",
                datetime.fromisoformat("2024-12-06 14:00"),
                datetime.fromisoformat("2024-12-12 18:00"),
                "Helsinki",
                3,
            ),
        ]

        self.vagtlister: list[VagtListe] = []
        self.create_vagtliste()

        tabControl = ttk.Notebook(self.root)

        self.tabs = {
            "Vagtperioder": VagtPeriodeTab(
                tabControl, self.vagtperioder, self.on_vagtperiode_update
            ),
            "Vagtliste": VagtListeTab(tabControl, self.vagtlister),
            "Afmønstringer": StatistikTab(tabControl),
            "Statistik": StatistikTab(tabControl),
            "Eksport": ExportTab(tabControl),
        }

        for key, value in self.tabs.items():
            tabControl.add(value, text=key)

        tabControl.pack(expand=1, fill="both")

    def create_vagtliste(self):
        self.vagtlister.clear()

        for vagtperiode in self.vagtperioder:
            nye_vagtperioder = vagtperiode.get_vagtliste_stubs()
            # TODO: Only create if not exists
            # self.vagtlister.extend()

    def on_vagtperiode_update(self):
        self.create_vagtliste()
        self.tabs["Vagtliste"].sync_list()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = App()
    app.run()
