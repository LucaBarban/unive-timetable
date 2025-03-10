import logging as log
from typing import List

import unive_timetable.config as cfg
from unive_timetable.lesson import Lesson
from unive_timetable.provider import Provider
from unive_timetable.providers.caldav_provider import CalDAV
from unive_timetable.providers.gcal_provider import GoogleCalendar
from unive_timetable.scraper import scrapeLessons
from unive_timetable.utils import compareEvents

if __name__ == "__main__":
    log.basicConfig(
        level=log.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        # filename="trace.log",
    )
    config = cfg.get()

    # url to scrape from
    ignore = config["general"]["ignore"]
    curriculum = config["general"]["curriculum"]
    updatePastEvents = config["general"]["updatePastEvents"]

    scrapedEvents: List[Lesson] = []
    for year in config["general"]["years"]:
        scrapedEvents = scrapedEvents + scrapeLessons(curriculum, year, ignore)
    log.info(f"{len(scrapedEvents)} events found")

    provider: Provider
    match config["general"]["provider"]:
        case "gcal":
            provider = GoogleCalendar(config)
        case "caldav":
            provider = CalDAV(config)
        case _:
            raise ValueError(f"No such provider: {config["general"]["provider"]}")

    deleteCals, newCals = compareEvents(
        scrapedEvents, provider.getEvents(), updatePastEvents
    )

    log.info(f"Found {len(newCals)} new Events and {len(deleteCals)} to delete")
    provider.deleteEvents(deleteCals)
    provider.createEvents(newCals)
