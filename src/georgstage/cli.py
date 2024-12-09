import logging
from georgstage.model import VagtPeriode
from datetime import datetime

logging.basicConfig(level=logging.INFO)

periode_1 = VagtPeriode(
    "Søvagt",
    datetime.fromisoformat("2024-12-02 10:00"),
    datetime.fromisoformat("2024-12-06 14:00"),
    "Korsør-Helsinki",
    2,
)

periode_1.get_vagtliste_dates()

periode_2 = VagtPeriode(
    "Havnevagt",
    datetime.fromisoformat("2024-12-06 14:00"),
    datetime.fromisoformat("2024-12-12 18:00"),
    "Korsør-Helsinki",
    2,
)

periode_2.get_vagtliste_dates()
