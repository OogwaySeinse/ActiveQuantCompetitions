from __future__ import annotations

from typing import Callable, Dict, List

from scraper.models import CompetitionRecord
from scraper.sources import (
    aicrowd,
    codalab,
    crunchdao,
    devpost,
    drivendata,
    ens,
    janestreet,
    kaggle,
    mlcontests,
    numerai,
    quantcontests,
    tianchi,
    zindi,
)

ScraperFn = Callable[[], List[CompetitionRecord]]

ALL_SCRAPERS: Dict[str, ScraperFn] = {
    "numerai": numerai.scrape,
    "crunchdao": crunchdao.scrape,
    "ens": ens.scrape,
    "janestreet": janestreet.scrape,
    "quantcontests": quantcontests.scrape,
    "kaggle": kaggle.scrape,
    "mlcontests": mlcontests.scrape,
    "zindi": zindi.scrape,
    "drivendata": drivendata.scrape,
    "aicrowd": aicrowd.scrape,
    "codalab": codalab.scrape,
    "devpost": devpost.scrape,
    "tianchi": tianchi.scrape,
}

