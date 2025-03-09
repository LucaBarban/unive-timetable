import logging as log

import unive_timetable.config as cfg
from unive_timetable.providers.tt_caldav import CalDAV
from unive_timetable.providers.tt_gcal import GoogleCalendar
from unive_timetable.scraper import scrapeLessons
from unive_timetable.utils import compareEvents


def main():
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

    scrapedEvents = []
    for year in config["general"]["years"]:
        scrapedEvents = scrapedEvents + scrapeLessons(curriculum, year, ignore)
    log.info(f"{len(scrapedEvents)} events found")

    if config["general"]["provider"] == "gcal":
        CREDENTIALS_FILE = config["gcal"]["credentials"]
        googleC = GoogleCalendar(CREDENTIALS_FILE, config)
        deleteCals, newCals = compareEvents(
            scrapedEvents, googleC.getFromGoogleCalendar(), updatePastEvents
        )
        log.info(f"Found {len(newCals)} new Events and {len(deleteCals)} to delete")
        googleC.deleteEvents(deleteCals)
        googleC.createEvents(newCals)

    if config["general"]["provider"] == "caldav":
        caldav = CalDAV(config)
        caldavEvents = caldav.getEvents()
        deleteCals, newCals = compareEvents(
            scrapedEvents, caldavEvents, updatePastEvents
        )
        log.info(f"Found {len(newCals)} new Events and {len(deleteCals)} to delete")
        caldav.deleteEvents(deleteCals)
        caldav.createEvents(newCals)


if __name__ == "__main__":
    main()
