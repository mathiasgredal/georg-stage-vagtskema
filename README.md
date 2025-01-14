# Georg Stage vagtplanlægger

Dette er et hjælpeprogram til vagtplanlægning ombord på Georg Stage.


BUGS:
- Validation should check for invalid numbers, hvis afmønstret, numre uden for skifte
- There can be duplicate landgangsvagter

MUST:
- Markering af ude numre f.eks. HU, Syg
- Print til pdf med dato-interval
- EASTER EGG: Play 6 bakke lyd når man trykker på 6. bakke

NICE TO HAVE:
- Forbedret dato-input
- Autosave
- Treeview indel i kolonner for listen af vagtperioder
- In vagtliste tab, only allow numbers input

- [DONE] Show all raised exception in message box

- [DONE] Fejl havnevagter: den samme elev kan have to nattevagter på samme nat i havn.
- [DONE] Tilføjelse: vagthavende elev får automatisk en vagt mellem 22-08 i havn. Da vagthavende elev ikke kan have vagt mellem 08-22. Ligesom dette ikke kan lade sig gøre for Dæks i kabys.
- [DONE] Angivelse af HU-numre, så de ikke får vagter mellem kl. 08-16 i havn. Der er maksimalt 8 elever, der kan have HU mellem 8-16 ad gangen.
- [DONE] Er det muligt at tilføje statistik over HU?
- [DONE] Er det muligt at tilføje statistik over vagter i havn/vagter på Holmen? Så man kan se hvor mange gange en elev har haft 8-12 vagten eller 6-8 vagten?
- [DONE] Programmet skal føre statestik over, hvem der har haft hvilke vagter i havn.
- [TODO] Holmen: Er det muligt at tilføje en knap, hvor man kan vælge mellem 1 eller to elever på nattevagt?
- [TODO] Er det muligt at tilføje en knap, hvor man kan fravælge dæks i kabys på Holmen?
- [TODO] Overgang fra Holmen/havn til søvagt: Dæks i kabys fra vagt skiftet bliver dæks i kabys mellem 8-12/8-15/15-20 af hængig af tidspunktet fra skiftet
- [TODO] Vagthavende elev: Rettelse: man kan ikke være vagthavende elev to gange i træk, hverken i havn eller i søen.
- [IN_PROGRESS] Tilvalg: Vagthavende elev er random eller Vagthavende elev er kronologisk, hvor man angiv start numrene for skifterne

