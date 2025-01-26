# Georg Stage Vagtplanlægger

Dette er et hjælpeprogram til vagtplanlægning ombord på Georg Stage. Programmet skemalægger ca. 27.000 timers arbejde på et togt, der finder sted to gange om året. Det er tilgængeligt for både Windows og MacOS, hvilket gør det nemt at tilgå for alle brugere. Programmet anvendes primært af 2. kvartermester, som har brug for at planlægge vagtplanlægningen effektivt.

## Skærmbilleder
|<img width="962" src="https://github.com/user-attachments/assets/2d06c3b6-bbb0-45af-85e9-9b73ead010b7" />|<img width="962" src="https://github.com/user-attachments/assets/34b60abd-7d83-4187-87f8-007574fb576c" />|
|-|-|
|<img width="962" src="https://github.com/user-attachments/assets/dc763b3e-5184-402c-ae6a-10e4dcf1c5e9" />|<img width="962" src="https://github.com/user-attachments/assets/f376032d-c78c-4cf3-8170-92547a1865d4" />|


## Installation
1. Installer Python 3.9 eller nyere.
2. Download zip-arkive med programmet [her](https://github.com/mathiasgredal/georg-stage-vagtskema/archive/refs/heads/main.zip).
3. Dekomprimer zip-arkivet, og naviger til mappen.
4. På Windows, dobbelt-klik på *start_win.bat*, på MacOS dobbelt-klik på *start_mac*.
5. *Valgfrit: Lav en genvej til en af de førnævnte filer, som så kan lægges på skrivebordet for hurtig adgang.*

## Anvendelse
1. Opret en vagtperiode, som specificerer en del af togtet.
    - Vælg vagttypen, start, slut
    - Specificer begyndende vagtskifte, for at vælge 08-12 vagten på søvagt eller begyndende skifte i vagttørnen i havn.
    - Vælg kronologisk vagthavende elev, som sørger for at vagthavende elev er i sekventiel numerisk orden. Hvis nr. 0 vælges så fortsættes sekvenses fra sidste vagtperiode, eller det første nr. i skiftet, hvis der ikke er tidligere vagtperioder.
    - Holmen: Hvis Holmen vælges som vagttype er der mulighed for at tilvælge dækselev i kabys, samt 2 nattevagter.
2.  Gå til "Vagtliste" for at se de producerede vagter, her kan eventuelle manuelle rettelser laves, og HU vagter kan indsættes.
3.  Herefter kan vagtskemaet gemmes ved at trykke på Ctrl+S eller i menuen.
4.  Til sidst kan man printe vagtskemaet ud ved at trykke på Ctrl+P.

## Tips og egenskaber
- Nogle invarianter kan ikke altid opholdes ved partielle opdateringer af vagtlisten, hvor man fjerner et enkelt nummer og trykker "Auto-Udfyld". I dette tilfælde kan alle vagtlister genskabes under "Vagtliste" siden, med den røde knap nederst til højre på listen.

- Når man skal indsætte HU elever, kan der nemt komme konflikter med de tildelte landgangsvagrter. I dette tilfælde kan man trykke på "Ryd" knappen og derefter "Auto-Udfyld", da "Ryd" funktionen bevarer HU numre. Generelt set vil HU numre bevares selvom vagtlisten og hele vagtperioden slettes og laves igen.

- Når man har indtastet en afmønstring for en given periode, vil programmet tjekke om der er elev-numre, som bør fjernes pga. den indtastede afmønstring. Er dette tilfældet, vises en knap "Opdater vagtlister...", som vil fjerne det specificeret elev-nr i denne periode og automatisk udfylde disse vagter.

- Hvis man vil ekskludere numre mere ad-hoc ved "Auto-Udfyld", kan man indtaste dem under "Ude" feltet på "Vagtliste" siden. 

- Hvis en dag er opdelt af f.eks. en havnevagt op til kl. 10 og en søvagt fra kl. 10 og videre, så vil programmet sammenflette disse 2 vagtlister til et samlet vagtskema for denne dag under eksport.

- Pejlegaster tildeles numre ud fra et princip om makkeroplæring, dvs. at den forrige pejlegast A, bliver pejlegast B, og der vælges en ny "tilfældig" pejlegast A. Dette er dog ikke altid muligt, f.eks. hvis der ikke er en tidligere pejlegast, nummeret er allerede tildelt manuelt, nummeret er afmønstret/ude, nummeret er valgt til kronologisk vagthavende, eller en anden grund, så vil 2 tilfældige numre vælges, da makker-oplæring ikke er muligt.

- Da tildeling af fysiske dagsvagter på søvagt forhindre deltagelse i undervisning, er det meget vigtigt at et nummer ikke vælges på en dagsvagt 2 gange i træk.

- Ved overgang mellem havnevagt og søvagt, genbruges dækseleven i kabys som allerede er tildelt for havnevagt til søvagten for det skifte som havde havnevagten. 

- Ved havnevagt kan vagthavende elev ikke stå landgangsvagt om dagen men kan godt om natte, og dækselev kan ikke stå landgangsvagt om dagen eller om natten.

- Det samme nummer kan ikke tildeles flere forskellige vagter, som kan være i konflikt med hinanden. Om vagter er i konflikt afhænger meget af vagterne samt tidspunkt.


- Hvis tidspunktet for en vagtperiode flyttes, vil de vagtlister som eksistere i både den gamle og nye periode bevares, samt manuelle ændringer i disse vagtlister. Hvis en ændring i vagtperioden gør at vagtlisten skal genskabes(type, nyt tidspunkt, begyndende skifte...), vil manuelle ændringer i vagtlisterne forsvinde ved genskabning.

## Genveje/Shortcuts
- Ctrl+S: Gem vagtskema
- Ctrl+O: Åben vagtskema
- Ctrl+P: Print vagtskeme, eller eksporter til PDF
- Ctrl+Z: Fortryd sidste handling (max. 50 handlinger kan fortrydes i træk)
- Ctrl+Y: Annuller fortrudt handling, forbeholdt ingen ændringer er foretaget

## Licens
Se [LICENSE.txt](https://github.com/mathiasgredal/georg-stage-vagtskema/blob/main/LICENCE.txt)

## Kontakt
Brug GitHub issues til at melde eventuelle fejl, mangler eller feature requests.

Jeg kan kontaktes på e-mail via. [mathias@gredal.dev](mathias@gredal.dev)

