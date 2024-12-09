from datetime import date, timedelta
import logging

from dateutil.parser import parse
import numpy as np

from georgstage.autofill import lp
from georgstage.model import GeorgStage, Vagt, Opgave, get_skifte_for_gast
from georgstage.view import View, LABELS

logger = logging.getLogger()


class Controller(object):
    """docstring for Controller."""

    def __init__(self, autofiller=lp.autofill):
        model = GeorgStage([])
        self.model = model
        self.view = View(self, model)
        self.autofiller = autofiller

    def main(self):
        logger.debug("In main of controller")
        self.view.main()

    def new_plan(self):
        logger.debug("New plan")

    def delete_date(self):
        current_date = self.view.get_current_date()
        try:
            dt = parse(current_date).date()
            header = "Slet dato"
            text = f"Er du sikker på at du vil slette {dt.isoformat()}?"
            if self.view.ask_consent(header, text):
                del self.model[dt]
                self.view.update()
        except Exception:
            self.view.show_warning("Fejl", "Kunne ikke slette dato")

    def reset_date(self):
        current_date = self.view.get_current_date()
        try:
            dt = parse(current_date).date()
            header = "Nulstil dato"
            text = f"Er du sikker på at du vil rydde alle vagter for {dt.isoformat()}?"
            if self.view.ask_consent(header, text):
                self.model[dt] = []
                self.view.update()
        except Exception:
            self.view.show_warning("Fejl", "Kunne ikke rydde vagter")

    def guess_pejlegast_a(self, dt):
        yesterday = dt - timedelta(days=1)
        logger.debug(f"{dt}, {yesterday}")
        logger.debug(f"Inspecting vagter {yesterday}: {self.model[yesterday]}")
        for vagt in self.model[yesterday]:
            if vagt.opgave == Opgave.PEJLEGAST_B:
                logger.debug(vagt)
                return Vagt(
                    dato=dt, vagt_tid=16, gast=vagt.gast, opgave=Opgave.PEJLEGAST_A
                )

    def guess_ude(self, dt):
        yesterday = dt - timedelta(days=1)
        logger.debug(f"{dt}, {yesterday}")
        logger.debug(f"Inspecting vagter {yesterday}: {self.model[yesterday]}")
        ude = []
        for vagt in self.model[yesterday]:
            if vagt.opgave == Opgave.UDE:
                logger.debug(vagt)
                ude.append(
                    Vagt(dato=dt, vagt_tid=-1, gast=vagt.gast, opgave=Opgave.UDE)
                )
        return ude

    def create_date(self):
        logger.debug("Creating date")
        self.persist_view()
        datoer = self.model.get_datoer()
        if len(datoer) > 0:
            max_dt = max(datoer)
            initial_value = max_dt + timedelta(days=1)
        else:
            initial_value = date.today()
        input_dato = self.view.ask_string(
            title="Opret dato",
            prompt="Indtast dato som skal oprettes (YYYY-MM-DD)",
            initial_value=initial_value.isoformat(),
        )
        try:
            new_dt = parse(input_dato).date()
        except Exception:
            self.view.show_warning(
                title="Fejl",
                message="Ugyldigt datoformat. Benyt venligst formatet YYYY-MM-DD, f.eks. 1935-4-24.",
            )
            return
        if new_dt in datoer:
            self.view.show_warning(title="Fejl", message="Dato findes i forvejen")
            return
        vagter = []
        # try to fill in pejlegast A as B from yesterday
        pejlegast_a = self.guess_pejlegast_a(new_dt)
        if pejlegast_a is not None:
            vagter.append(pejlegast_a)
        ude = self.guess_ude(new_dt)
        for vagt in ude:
            vagter.append(vagt)
        self.model[new_dt] = vagter
        self.model.set_current_dato(new_dt)
        self.view.update()

    def change_date(self, new_date):
        logger.debug("Changing date")
        self.persist_view()
        self.model.set_current_dato(new_date)
        self.view.update()

    def persist_view(self):
        """
        Store fields from view in model
        """
        logger.debug("Persisting view")
        # translate dt and export_vars to vagter
        dt = self.model.get_current_dato()
        if dt is None:
            logger.debug("Current date not set, persist skipped")
            return
        export_vars = self.view.get_vars()
        vagter = [
            Vagt(dato=dt, vagt_tid=vagt_tid, gast=int(gast), opgave=opgave)
            for (opgave, vagt_tid), gast in export_vars
            if gast.isdigit()
        ]
        self.model[dt] = vagter

    def _guess_skifter(self, vagter):
        logger.debug("Guessing skifter")
        guesses = [None, None, None, None, None, None]
        for vagt in vagter:
            if vagt.opgave == Opgave.UDE:
                continue
            skifte = get_skifte_for_gast(vagt.gast)
            idx = vagt.vagt_tid // 4
            guesses[idx] = skifte
        return guesses

    def export_word(self):
        logger.debug("Exporting to word")
        self.view.show_info(
            "Eksporter til word", "Eksporter til word er ikke implementeret endnu"
        )

    def open_file(self):
        logger.debug("Opening file")
        try:
            filepath = self.view.ask_open_file(
                filetypes=[("Georg Stage Vagtplan", "*.gsv")]
            )
            logger.debug(f"loading file: {filepath}")
            model = GeorgStage.load(filepath)
            self.model = model
            self.view.set_model(model)
            self.view.update()
        except Exception as e:
            logger.exception(e)
            self.view.show_warning(
                "Fejl",
                "Der opstod en fejl under forsøget på at åbne din vagtplan. Check filformatet og prøv igen.",
            )

    def save_file_as(self):
        try:
            filepath = self.view.ask_save_file_as(
                defaultextension="gsv", filetypes=[("Georg Stage Vagtplan", "*.gsv")]
            )
            if filepath is not None:
                logger.debug(f"Saving file: {filepath}")
                self.persist_view()
                self.model.save(filepath)
                self.view.show_info("Fil gemt", "Din vagtplan er blevet gemt")
        except Exception as e:
            logger.exception(e)
            self.view.show_warning(
                "Fejl", "Der opstod en fejl under forsøget på at gemme din vagtplan"
            )

    def get_help(self):
        header = "Hjælp"
        text = "Version 0.2.1. Læs mere på hjemmesiden https://github.com/skipperkongen/georgstage"
        self.view.show_info(header, text)

    def autofill(self):
        logger.debug("Fill day clicked")
        try:
            dt = self.model.get_current_dato()
            self.persist_view()
            vagter = self.model[dt]
            skifter = self._guess_skifter(vagter)
            logger.debug(f"Guesses: {skifter}")
            for i, skifte in enumerate(skifter):
                if skifte is None:
                    header = "Angiv skifte"
                    text = f"Hvilket skifte har vagt fra klokken {str(i*4).zfill(2)} - {str((i+1)*4).zfill(2)}"
                    skifte = self.view.ask_number(header, text)
                    if skifte not in (1, 2, 3):
                        raise ValueError(f"Skifte {skifte} not one of 1, 2, 3")
                    skifter[i] = skifte
            logger.debug(f"Skifter: {skifter}")
            fill_result = self.autofiller(self.model, skifter)
            logger.debug(fill_result)
            if fill_result.status != 1:
                raise ValueError("Tjek at vagtplan er korrekt udfyldt")
            self.model[dt] = fill_result.vagter
            self.view.update()

        except Exception as e:
            logger.exception(e)
            self.view.show_warning(
                "Fejl", f"Vagtplanen kan ikke udfyldes automatisk: {e}"
            )

    def show_stats(self):
        logger.debug("Show stats clicked")
        gast = self.view.ask_number("Vis statistik", "Indtast gast")
        df = self.model.to_dataframe()
        s = df[df.gast == gast].groupby(df.opgave).count().opgave
        n_vagthavende = s.get("VAGTHAVENDE_ELEV") or 0
        n_fysisk = (
            (s.get("ORDONNANS") or 0)
            + (s.get("UDKIG") or 0)
            + (s.get("BJAERGEMAERS") or 0)
            + (s.get("RORGAENGER") or 0)
        )
        n_kabys = s.get("DAEKSELEV_I_KABYS") or 0
        n_pejlegast = (s.get("PEJLEGAST_A") or 0) + (s.get("PEJLEGAST_B") or 0)
        n_udsaet = (
            (s.get("UDSAETNINGSGAST_A") or 0)
            + (s.get("UDSAETNINGSGAST_B") or 0)
            + (s.get("UDSAETNINGSGAST_C") or 0)
            + (s.get("UDSAETNINGSGAST_D") or 0)
            + (s.get("UDSAETNINGSGAST_E") or 0)
        )
        n_ude = s.get("UDE") or 0

        col_labels = ["Antal gange"]
        row_labels = [
            "Vagthavende elev",
            "Fysisk vagt",
            "Kabys",
            "Pejlegast",
            "Udsætningsgast",
            "Ude/HU",
        ]
        rows = np.expand_dims(
            [n_vagthavende, n_fysisk, n_kabys, n_pejlegast, n_udsaet, n_ude], axis=1
        )

        self.view.show_table(rows, col_labels, row_labels, header="Statistik for gast")
