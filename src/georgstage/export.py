import webbrowser
import base64
from georgstage.solver import søvagt_skifte_for_vagttid
from georgstage.model import VagtTid, Opgave, VagtListe
from tkinter import messagebox as mb
from copy import deepcopy
import tempfile

class Exporter:
    def export_vls(self, input_vls: list[VagtListe]) -> None:
        if len(input_vls) == 0:
            mb.showerror('Fejl', 'Ingen vagtlisteer at eksportere')
            return
        input_vls = deepcopy(input_vls)

        vls = []
        current_vl = input_vls[0]
        for next_vl in input_vls[1:]:
            if current_vl.get_date() == next_vl.get_date() and current_vl.vagttype != next_vl.vagttype:
                current_vl.vagter.update(next_vl.vagter)
                current_vl.end = next_vl.end
            else:
                vls.append(current_vl)
                current_vl = next_vl
        vls.append(current_vl)

        html_table = f"""
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <title>Georg Stage - Vagtskema</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <script type="text/javascript">
    window.onload = function () {{
      window.print();
    }}
  </script>

  <style type="text/css">
    body {{
      font-family: Sans-Serif;
    }}

    table {{
      border-collapse: collapse;
      width: 100%;
    }}

    td {{
      border: 1px solid black;
      padding-left: 4px;
      padding-right: 4px;
      font-size: medium;
      font-style: italic;
      text-align: center;
      vertical-align: top
    }}

    tr {{
      line-height: 24px;
    }}

    .tg-bold {{
      font-size: small;
      font-weight: bold;
      text-align: left;
      vertical-align: top;
      font-style: normal;
    }}

    .tg-xl {{
      font-size: medium;
      text-align: left;
      vertical-align: top;
      font-style: normal;
    }}

    .tg-label {{
      font-size: small;
      text-align: left;
      vertical-align: top;
      font-style: normal;
    }}

    .tg-center {{
      text-align: center;
    }}

    .slim-row {{
      line-height: 16px;
    }}

    @page {{
      size: auto;
      margin: 0;
    }}

    @media print {{
        .pagebreak {{ clear: both; page-break-before: always; }}
    }}
  </style>
</head>

<body>
  <center>
   {'<div class="pagebreak"> </div>'.join(self.make_vl_fragment(vl) for vl in vls)}
  </center>
</body>

</html>
        """

        # We get a pathlength error on windows, so we use a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as f:
            f.write(html_table.encode())
            f.flush()
            f.close()
            print(f.name)
            webbrowser.open(f"file://{f.name}", new=1, autoraise=True)

    def make_vl_fragment(self, vl: VagtListe) -> str:
        weekdays = ['mandag', 'tirsdag', 'onsdag', 'torsdag', 'fredag', 'lørdag', 'søndag']
        return f"""
    <h2>Vagtskema: Fra {weekdays[vl.get_date().weekday()]} d. {vl.get_date().strftime('%d/%m')} til {weekdays[vl.end.weekday()]} d. {vl.end.strftime('%d/%m')}</h2>
    <table style="table-layout: fixed; width: 574px; border: 2px solid black">
      <colgroup>
        <col style="width: 150px">
        <col style="width: 37px">
        <col style="width: 37px">
        <col style="width: 37px">
        <col style="width: 37px">
        <col style="width: 37px">
        <col style="width: 37px">
        <col style="width: 37px">
        <col style="width: 37px">
        <col style="width: 37px">
        <col style="width: 37px">
        <col style="width: 37px">
        <col style="width: 37px">
      </colgroup>
      <tbody>
        <tr>
          <td class="tg-bold">Havne-/Ankervagt</td>
          <td colspan="12"></td>
        </tr>
        <tr>
          <td class="tg-label">Kvartermester (8-17)</td>
          <td colspan="4"></td>
          <td class="tg-label" colspan="4">Kvartermester (17-22)</td>
          <td colspan="4"></td>
        </tr>
        <tr>
          <td class="tg-label" class="tg">ELEV vagtskifte</td>
          <td colspan="4">{f'{vl.starting_shift.value}#' if VagtTid.ALL_DAY in vl.vagter else ''}</td>
          <td class="tg-label" colspan="4">Vagthavende ELEV</td>
          <td colspan="4">{self.get_nr(vl, VagtTid.ALL_DAY, Opgave.VAGTHAVENDE_ELEV)}</td>
        </tr>
        <tr class="slim-row">
          <td class="tg-bold">Rutiner</td>
          <td colspan="12"></td>
        </tr>
        <tr>
          <td class="tg-label">Rengøring på DÆK</td>
          <td colspan="4"></td>
          <td class="tg-label" colspan="4">Badedag</td>
          <td colspan="4"></td>
        </tr>
        <tr>
          <td class="tg-label">Rengøring om LÆ</td>
          <td colspan="4"></td>
          <td class="tg-label" colspan="4">Fartøjstjeneste</td>
          <td colspan="4"></td>
        </tr>
        <tr class="slim-row">
          <td class="tg-bold">Tider</td>
          <td class="tg-label tg-center">08 - 10</td>
          <td class="tg-label tg-center">10 - 12</td>
          <td class="tg-label tg-center">12 - 14</td>
          <td class="tg-label tg-center">14 - 16</td>
          <td class="tg-label tg-center">16 - 18</td>
          <td class="tg-label tg-center">18 - 20</td>
          <td class="tg-label tg-center">20 - 22</td>
          <td class="tg-label tg-center">22 - 24</td>
          <td class="tg-label tg-center">00 - 02</td>
          <td class="tg-label tg-center">02 - 04</td>
          <td class="tg-label tg-center">04 - 06</td>
          <td class="tg-label tg-center">06 - 08</td>
        </tr>
        <tr>
          <td class="tg-label">Vagthavende ELEV</td>
          <td colspan="2"></td>
          <td colspan="2"></td>
          <td colspan="2"></td>
          <td colspan="2"></td>
          <td colspan="2"></td>
          <td colspan="2"></td>
        </tr>
        <tr>
          <td class="tg-label">Radio- / Landgangsvagt</td>
          <td>{self.get_nr(vl, VagtTid.T08_12, Opgave.LANDGANGSVAGT_A)}</td>
          <td>{self.get_nr(vl, VagtTid.T08_12, Opgave.LANDGANGSVAGT_A)}</td>
          <td>{self.get_nr(vl, VagtTid.T12_16, Opgave.LANDGANGSVAGT_A)}</td>
          <td>{self.get_nr(vl, VagtTid.T12_16, Opgave.LANDGANGSVAGT_A)}</td>
          <td>{self.get_nr(vl, VagtTid.T16_18, Opgave.LANDGANGSVAGT_A)}</td>
          <td>{self.get_nr(vl, VagtTid.T18_20, Opgave.LANDGANGSVAGT_A)}</td>
          <td>{self.get_nr(vl, VagtTid.T20_22, Opgave.LANDGANGSVAGT_A)}</td>
          <td>{self.get_nr(vl, VagtTid.T22_00, Opgave.LANDGANGSVAGT_A)}</td>
          <td>{self.get_nr(vl, VagtTid.T00_02, Opgave.LANDGANGSVAGT_A)}</td>
          <td>{self.get_nr(vl, VagtTid.T02_04, Opgave.LANDGANGSVAGT_A)}</td>
          <td>{self.get_nr(vl, VagtTid.T04_06, Opgave.LANDGANGSVAGT_A)}</td>
          <td>{self.get_nr(vl, VagtTid.T06_08, Opgave.LANDGANGSVAGT_A)}</td>
        </tr>
        <tr>
          <td class="tg-label">Udkig / Landgangsvagt</td>
          <td>{self.get_nr(vl, VagtTid.T08_12, Opgave.LANDGANGSVAGT_B)}</td>
          <td>{self.get_nr(vl, VagtTid.T08_12, Opgave.LANDGANGSVAGT_B)}</td>
          <td>{self.get_nr(vl, VagtTid.T12_16, Opgave.LANDGANGSVAGT_B)}</td>
          <td>{self.get_nr(vl, VagtTid.T12_16, Opgave.LANDGANGSVAGT_B)}</td>
          <td>{self.get_nr(vl, VagtTid.T16_18, Opgave.LANDGANGSVAGT_B)}</td>
          <td>{self.get_nr(vl, VagtTid.T18_20, Opgave.LANDGANGSVAGT_B)}</td>
          <td>{self.get_nr(vl, VagtTid.T20_22, Opgave.LANDGANGSVAGT_B)}</td>
          <td>{self.get_nr(vl, VagtTid.T22_00, Opgave.LANDGANGSVAGT_B)}</td>
          <td>{self.get_nr(vl, VagtTid.T00_02, Opgave.LANDGANGSVAGT_B)}</td>
          <td>{self.get_nr(vl, VagtTid.T02_04, Opgave.LANDGANGSVAGT_B)}</td>
          <td>{self.get_nr(vl, VagtTid.T04_06, Opgave.LANDGANGSVAGT_B)}</td>
          <td>{self.get_nr(vl, VagtTid.T06_08, Opgave.LANDGANGSVAGT_B)}</td>
        </tr>
        <tr>
          <td class="tg-label">Pejlegast A/B</td>
          <td colspan="2"></td>
          <td colspan="2"></td>
          <td colspan="2"></td>
          <td colspan="2"></td>
          <td colspan="2"></td>
          <td colspan="2"></td>
        </tr>
        <tr>
          <td class="tg-label">Dækselev i kabys</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.ALL_DAY, Opgave.DAEKSELEV_I_KABYS)}</td>
          <td colspan="2"></td>
          <td colspan="2"></td>
          <td colspan="2"></td>
          <td colspan="2"></td>
          <td colspan="2"></td>
        </tr>
        <tr>
          <td class="tg-label">HU</td>
          <td colspan="2"></td>
          <td colspan="2"></td>
          <td colspan="2"></td>
          <td colspan="2"></td>
          <td colspan="2"></td>
          <td colspan="2"></td>
        </tr>
        <tr style="border-top: 2px solid black">
          <td class="tg-bold">Søvagt</td>
          <td class="tg-label tg-center" colspan="2">08-12</td>
          <td class="tg-label tg-center" colspan="2">12-15</td>
          <td class="tg-label tg-center" colspan="2">15-20</td>
          <td class="tg-label tg-center" colspan="2">20-24</td>
          <td class="tg-label tg-center" colspan="2">00-04</td>
          <td class="tg-label tg-center" colspan="2">04-08</td>
        </tr>
        <tr>
          <td class="tg-label">ELEV vagtskifte</td>
          <td colspan="2">{self.get_skifte(vl, VagtTid.T08_12)}</td>
          <td colspan="2">{self.get_skifte(vl, VagtTid.T12_15)}</td>
          <td colspan="2">{self.get_skifte(vl, VagtTid.T15_20)}</td>
          <td colspan="2">{self.get_skifte(vl, VagtTid.T20_24)}</td>
          <td colspan="2">{self.get_skifte(vl, VagtTid.T00_04)}</td>
          <td colspan="2">{self.get_skifte(vl, VagtTid.T04_08)}</td>
        </tr>
        <tr>
          <td class="tg-label">Vagthavende ELEV</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T08_12, Opgave.VAGTHAVENDE_ELEV)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T12_15, Opgave.VAGTHAVENDE_ELEV)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T15_20, Opgave.VAGTHAVENDE_ELEV)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T20_24, Opgave.VAGTHAVENDE_ELEV)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T00_04, Opgave.VAGTHAVENDE_ELEV)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T04_08, Opgave.VAGTHAVENDE_ELEV)}</td>
        </tr>
        <tr>
          <td class="tg-label">Ordonnans</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T08_12, Opgave.ORDONNANS)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T12_15, Opgave.ORDONNANS)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T15_20, Opgave.ORDONNANS)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T20_24, Opgave.ORDONNANS)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T00_04, Opgave.ORDONNANS)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T04_08, Opgave.ORDONNANS)}</td>
        </tr>
        <tr>
          <td class="tg-label">Udkig</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T08_12, Opgave.UDKIG)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T12_15, Opgave.UDKIG)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T15_20, Opgave.UDKIG)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T20_24, Opgave.UDKIG)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T00_04, Opgave.UDKIG)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T04_08, Opgave.UDKIG)}</td>
        </tr>
        <tr>
          <td class="tg-label">Radiovagt</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T08_12, Opgave.RADIOVAGT)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T12_15, Opgave.RADIOVAGT)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T15_20, Opgave.RADIOVAGT)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T20_24, Opgave.RADIOVAGT)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T00_04, Opgave.RADIOVAGT)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T04_08, Opgave.RADIOVAGT)}</td>
        </tr>
        <tr>
          <td class="tg-label">Rorgænger</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T08_12, Opgave.RORGAENGER)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T12_15, Opgave.RORGAENGER)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T15_20, Opgave.RORGAENGER)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T20_24, Opgave.RORGAENGER)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T00_04, Opgave.RORGAENGER)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T04_08, Opgave.RORGAENGER)}</td>
        </tr>
        <tr>
          <td class="tg-label">Udsætningsgast A</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T08_12, Opgave.UDSAETNINGSGAST_A)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T12_15, Opgave.UDSAETNINGSGAST_A)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T15_20, Opgave.UDSAETNINGSGAST_A)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T20_24, Opgave.UDSAETNINGSGAST_A)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T00_04, Opgave.UDSAETNINGSGAST_A)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T04_08, Opgave.UDSAETNINGSGAST_A)}</td>
        </tr>
        <tr>
          <td class="tg-label">Udsætningsgast B</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T08_12, Opgave.UDSAETNINGSGAST_B)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T12_15, Opgave.UDSAETNINGSGAST_B)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T15_20, Opgave.UDSAETNINGSGAST_B)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T20_24, Opgave.UDSAETNINGSGAST_B)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T00_04, Opgave.UDSAETNINGSGAST_B)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T04_08, Opgave.UDSAETNINGSGAST_B)}</td>
        </tr>
        <tr>
          <td class="tg-label">Udsætningsgast C</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T08_12, Opgave.UDSAETNINGSGAST_C)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T12_15, Opgave.UDSAETNINGSGAST_C)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T15_20, Opgave.UDSAETNINGSGAST_C)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T20_24, Opgave.UDSAETNINGSGAST_C)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T00_04, Opgave.UDSAETNINGSGAST_C)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T04_08, Opgave.UDSAETNINGSGAST_C)}</td>
        </tr>
        <tr>
          <td class="tg-label">Udsætningsgast D</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T08_12, Opgave.UDSAETNINGSGAST_D)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T12_15, Opgave.UDSAETNINGSGAST_D)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T15_20, Opgave.UDSAETNINGSGAST_D)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T20_24, Opgave.UDSAETNINGSGAST_D)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T00_04, Opgave.UDSAETNINGSGAST_D)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T04_08, Opgave.UDSAETNINGSGAST_D)}</td>
        </tr>
        <tr>
          <td class="tg-label">Udsætningsgast E</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T08_12, Opgave.UDSAETNINGSGAST_E)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T12_15, Opgave.UDSAETNINGSGAST_E)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T15_20, Opgave.UDSAETNINGSGAST_E)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T20_24, Opgave.UDSAETNINGSGAST_E)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T00_04, Opgave.UDSAETNINGSGAST_E)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T04_08, Opgave.UDSAETNINGSGAST_E)}</td>
        </tr>
        <tr>
          <td class="tg-label">Pejlegast A/B</td>
          <td colspan="2">{self.get_pejlegast(vl, VagtTid.T08_12)}</td>
          <td colspan="2">{self.get_pejlegast(vl, VagtTid.T12_15)}</td>
          <td colspan="2">{self.get_pejlegast(vl, VagtTid.T15_20)}</td>
          <td colspan="2">{self.get_pejlegast(vl, VagtTid.T20_24)}</td>
          <td colspan="2">{self.get_pejlegast(vl, VagtTid.T00_04)}</td>
          <td colspan="2">{self.get_pejlegast(vl, VagtTid.T04_08)}</td>
        </tr>
        <tr>
          <td class="tg-label">Dækselev i kabys</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T08_12, Opgave.DAEKSELEV_I_KABYS)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T12_15, Opgave.DAEKSELEV_I_KABYS)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T15_20, Opgave.DAEKSELEV_I_KABYS)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T20_24, Opgave.DAEKSELEV_I_KABYS)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T00_04, Opgave.DAEKSELEV_I_KABYS)}</td>
          <td colspan="2">{self.get_nr(vl, VagtTid.T04_08, Opgave.DAEKSELEV_I_KABYS)}</td>
        </tr>
      </tbody>
    </table>
        """

    def get_nr(self, vl: VagtListe, tid: VagtTid, opgave: Opgave) -> str:
        if tid not in vl.vagter:
            return ''
        if opgave not in vl.vagter[tid].opgaver:
            return ''
        return str(vl.vagter[tid].opgaver[opgave])

    def get_skifte(self, vl: VagtListe, tid: VagtTid) -> str:
        if VagtTid.ALL_DAY in vl.vagter or tid not in vl.vagter:
            return ''
        return str(søvagt_skifte_for_vagttid(vl.starting_shift, tid).value) + '#'

    def get_pejlegast(self, vl: VagtListe, tid: VagtTid) -> str:
        if tid not in vl.vagter:
            return ''
        if Opgave.PEJLEGAST_A in vl.vagter[tid].opgaver and Opgave.PEJLEGAST_B in vl.vagter[tid].opgaver:
            return (
                str(vl.vagter[tid].opgaver[Opgave.PEJLEGAST_A])
                + ' / '
                + str(vl.vagter[tid].opgaver[Opgave.PEJLEGAST_B])
            )
        elif Opgave.PEJLEGAST_A in vl.vagter[tid].opgaver:
            return str(vl.vagter[tid].opgaver[Opgave.PEJLEGAST_A])
        elif Opgave.PEJLEGAST_B in vl.vagter[tid].opgaver:
            return str(vl.vagter[tid].opgaver[Opgave.PEJLEGAST_B])
        return ''
