# Georg Stage vagtplanlægger

Dette er et hjælpeprogram til vagtplanlægning ombord på Georg Stage (søvagter).
Matematikken bag programmet benytter lineær programming (LP) til at optimere vagterne,
således at alle opgaver varetages, samtidigt med at opgaverne fordeles mellem
gasterne så fair som muligt. Programmet er skrevet i Python 3.

> Minimum Python version: 3.9



BUGS:
- Validation should check for invalid numbers, hvis afmønstret, numre uden for skifte
- There can be duplicate landgangsvagter

MUST:
- Markering af ude numre f.eks. HU, Syg
- Holmen
- Print til pdf med dato-interval
- EASTER EGG: Play 6 bakke lyd når man trykker på 6. bakke

NICE TO HAVE:
- Forbedret dato-input
- Autosave
- Treeview indel i kolonner for listen af vagtperioder
- In vagtliste tab, only allow numbers input
