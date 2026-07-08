"""Scraper registry."""

from crawler.scrapers.base import BaseScraper
from crawler.scrapers.company_sites import CompanySitesScraper
from crawler.scrapers.guopin import GuopinScraper
from crawler.scrapers.guopin_company import GuopinCompanyScraper
from crawler.scrapers.mot_recruit import MotRecruitScraper
from crawler.scrapers.nra_recruit import NraRecruitScraper
from crawler.scrapers.sasac import SasacScraper

SCRAPERS: dict[str, type[BaseScraper]] = {
    "guopin": GuopinScraper,
    "guopin_company": GuopinCompanyScraper,
    "mot_recruit": MotRecruitScraper,
    "nra_recruit": NraRecruitScraper,
    "sasac": SasacScraper,
    "company_sites": CompanySitesScraper,
}

__all__ = ["SCRAPERS", "BaseScraper"]
