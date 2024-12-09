# Georg Stage vagtplanlægger

Dette er et hjælpeprogram til vagtplanlægning ombord på Georg Stage (søvagter).
Matematikken bag programmet benytter lineær programming (LP) til at optimere vagterne,
således at alle opgaver varetages, samtidigt med at opgaverne fordeles mellem
gasterne så fair som muligt. Programmet er skrevet i Python 3.

> Minimum Python version: 3.7

Se [Kanban](https://github.com/users/skipperkongen/projects/2/) for opgaver der p.t. er igang.

## Installation

### Mac OS X and Windows

Installation med pip:

```shell
pip install georgstage --no-cache-dir
```

Kør:

```shell
python -m georgstage
```

### Raspberry Pi

Installation af dependencies:

```shell
sudo apt-get install libatlas-base-dev
sudo apt-get install glpk-utils
sudo pip install georgstage
sudo pulptest
```


## Lokal udvikling

```shell
python3 -m venv venv
source venv/bin/activate
pip install -e '.[tests]'
```

Kør tests:

```shell
make lint
make test
```

Start program:

```shell
make run_local
# or
python -m georgstage
```

## Publicer ny version

1. opdater versionsnummer i pyproject.toml
1. git commit -am 'besked'
1. git push
1. [På GitHub] opret ny release med matchende versionsnummer (tag og navn), dog med 'v' prefix.

Herefter offentliggøres ny version automatisk på PyPI via en Github Action.  

## Brugervejledning

Spørg Kostas

### Kode eksempler

Hvis du kan kode Python, kan du bruge Georg Stages API via kode.

*Auto-udfyldning:*

```python
from georgstage import GeorgStage, Opgave, Vagt
import pandas as pd

# initialiser GeorgStage med kode
vagter = [
    Vagt(dato='2021-05-01', vagt_tid=0, gast=1, opgave=Opgave.VAGTHAVENDE_ELEV),
    Vagt(dato='2021-05-01', vagt_tid=0, gast=2, opgave=Opgave.ORDONNANS),
    Vagt(dato='2021-05-01', vagt_tid=0, gast=3, opgave=Opgave.RORGAENGER),    
    Vagt(dato='2021-05-01', vagt_tid=0, gast=4, opgave=Opgave.UDKIG)
]
gs = GeorgStage(vagter)

# fyld et par uger ud automatisk
for dt in pd.date_range(start='2021-05-01', end='2021-05-14', closed=None).date:
    print(dt)
    fill_result = gs.autofill(dt)
    if fill_result.status == 1:
        gs[dt] = fill_result.vagter

# Check antal dage:
print(f'Antal dage = {len(gs)}')
```

*Load og save:*

```python
# Create gs from other gs
gs2 = GeorgStage(gs.get_vagter())

# Create gs from dataframe
gs3 = GeorgStage.from_dataframe(gs.to_dataframe())

# Save GeorgStage til file
gs.to_dataframe().to_csv('vagter.csv', index=False)

# Load GeorgStage fra file (CSV)
df_vagter = pd.read_csv('vagter.csv')
gs4 = GeorgStage.from_dataframe(df_vagter)
```

*Diverse:*

```python
# Eksporter som dataframe (Pandas)
gs.to_dataframe()

# Eksporter som liste af vagter
gs.get_vagter()

# Eksporter datoer
gs.get_datoer()
```

## Regler vedr. vagter på Georg Stage


Regler for søvagter, som gælder delvist for ankervagter:

- Elever er organiseret i 3 skifter (holod) med 20 gaster (elever) på hver
  - Skifte 1: gaster 1-20
  - Skifte 2: gaster 21-40
  - Skifte 3: Gaster 41-60
- Gaster 61-63 er kokke elever og er altid i køkkenet.
- Vagterne er går igen i 6 perioder per dag, som fordeles på skifte 1-3, så hver
skifte får to perioder per dag
  - Klokken 00 - 04
  - Klokken 04 - 08
  - Klokken 08 - 12
  - Klokken 12 - 16
  - Klokken 16 - 20
  - Klokken 20 - 24
- Det skal være fair, så alle få alle poster cirka lige mange gange
- De faste vagter er
  - Der er 1 kvartermester til hver skifte
  - Der er 1 udkig til hver skifte  
  - Der er 1 rorgænger til hver skifte    
  - Der er 1 ordonnans til hver skifte    
  - Der er 1 vagthavende elev til hver skifte
- De særlige vagter er:
  - Der er 1 dækselev i kabys, kun 8-12 (morgenmad), 12-16 (frokost), 16-20 (aftensmad)  
  - Den vagthavende elev er den samme gast både morgen og aften, går på tur, dag for dag, også når skifterne får nye vagter.
  - Pejlegast A fra dagen før, er pejlegast B dagen efter.
  - pejlegaster findes kun på 16-20 vagten
  - Der er udvalgte gaster der udtages til håndværksmæssig uddannelse hver dag.

Der findes også ankervagter, men det kører en smule anderledes.


