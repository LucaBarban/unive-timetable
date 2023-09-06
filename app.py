from unive_timetable.utils import Config, compareEvents
from unive_timetable.scraper import scrapeLessons
from unive_timetable.providers.tt_gcal import GoogleCalendar
from unive_timetable.providers.tt_caldav import CalDAV
from unive_timetable.providers.tt_ics import saveToIcs

def main():
    config = Config().getData()

    # url to scrape from
    ignore = config["general"]["ignore"]
    updatePastEvents = config['general']['updatePastEvents']

    oraribetter = []
    for year in config["general"]["years"]:
        url = "https://www.unive.it/data/it/1592/orario-lezioni/" + year
        oraribetter = oraribetter + scrapeLessons(url, ignore)
    print(str(len(oraribetter)) + " events found")

    if config["general"]["provider"] == "gcal":
        CREDENTIALS_FILE = config["gcal"]["credentials"]
        googleC = GoogleCalendar(CREDENTIALS_FILE, config)
        deleteCals, newCals = compareEvents(oraribetter, googleC.getFromGoogleCalendar(), updatePastEvents)
        print("Found", len(newCals), "new Events and", len(deleteCals), "to delete")
        googleC.deleteEvents(deleteCals)
        googleC.createEvents(newCals)

    if config["general"]["provider"] == "caldav":
        caldav = CalDAV(config)
        deleteCals, newCals = compareEvents(oraribetter, caldav.getEvents(), updatePastEvents)
        # print(caldav.getEvents()[0])
        print("Found", len(newCals), "new Events and", len(deleteCals), "to delete")
        caldav.deleteEvent(deleteCals)
        caldav.createEvent(newCals)

    if config["general"]["provider"] == "ics":
        saveToIcs(oraribetter, updatePastEvents)

if __name__ == "__main__":
    main()