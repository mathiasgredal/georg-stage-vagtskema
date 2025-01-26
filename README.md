# Georg Stage vagtplanlægger

Dette er et hjælpeprogram til vagtplanlægning ombord på Georg Stage.


- [DONE] Show all raised exception in message box

- [DONE] Fejl havnevagter: den samme elev kan have to nattevagter på samme nat i havn.
- [DONE] Tilføjelse: vagthavende elev får automatisk en vagt mellem 22-08 i havn. Da vagthavende elev ikke kan have vagt mellem 08-22. Ligesom dette ikke kan lade sig gøre for Dæks i kabys.
- [DONE] Angivelse af HU-numre, så de ikke får vagter mellem kl. 08-16 i havn. Der er maksimalt 8 elever, der kan have HU mellem 8-16 ad gangen.
- [DONE] Er det muligt at tilføje statistik over HU?
- [DONE] Er det muligt at tilføje statistik over vagter i havn/vagter på Holmen? Så man kan se hvor mange gange en elev har haft 8-12 vagten eller 6-8 vagten?
- [DONE] Programmet skal føre statestik over, hvem der har haft hvilke vagter i havn.
- [DONE] Tilvalg: Vagthavende elev er random eller Vagthavende elev er kronologisk, hvor man angiv start numrene for skifterne
    - Begrænsning: Hvis der er en pejlegast som er i konflikt med den kronologiske vagthavende elev, så genereres begge pejlegasterne på ny tilfældigt
    - Begrænsing: I overgang fra havn/holmen til søvagt, hvis vagthavende elev på søvagten er i konflikt med dækselev i kabys fra tidligere havnevagt, så laves der bare en tilfældig dækselev i kabys
    - Det er rigtig svært at lave delvise opdateringer af vagtlister, hvis der er en kronologisk vagthavende elev. Har lavet en knap til at genskabe alle vagter i vagtlisten, så den kronologiske orden bliver opdateret. Ulempen er at eventuelle manuelle ændringer bliver overskrevet.
- [DONE] Holmen: Er det muligt at tilføje en knap, hvor man kan vælge mellem 1 eller to elever på nattevagt?
- [DONE] Er det muligt at tilføje en knap, hvor man kan fravælge dæks i kabys på Holmen?
- [Done] Overgang fra Holmen/havn til søvagt: Dæks i kabys fra vagt skiftet bliver dæks i kabys mellem 8-12/8-15/15-20 afhængig af tidspunktet fra skiftet
- [Done] Vagthavende elev: Rettelse: man kan ikke være vagthavende elev to gange i træk, hverken i havn eller i søen.

Begrænsing:
- Hvis en væsentlig stor periode med afmønstring laves, og eleven genoptages, så vil den person få rigtig mange vagter, pga. måden vagter bliver valgt. Er dette et problem?


