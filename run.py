import configparser
import mycaldav as caldav
import utils

from scraper import scrapeLessons
from gcal import GoogleCalendar
from compareEvents import compareEvents
from calendarToIcs import saveToIcs

if utils.setup_config():
    config = configparser.ConfigParser()
    config.read("config.toml")
    # url to scrape from
    url = "https://www.unive.it/data/46/" + config["general"]["year"]
    ignore = config["general"]["ignore"]
    updatePastEvents = config['general']['updatePastEvents'] == "true" #conversion from str to bool

    oraribetter = scrapeLessons(url, ignore)
    print(str(len(oraribetter)) + " events found")

    if config["general"]["provider"] == "gcal":
        CREDENTIALS_FILE = config["gcal"]["credentials"]
        googleC = GoogleCalendar(CREDENTIALS_FILE)
        deleteCals, newCals = compareEvents(oraribetter, googleC.getFromGoogleCalendar(), updatePastEvents)
        print("Found", len(newCals), "new Events and", len(deleteCals), "to delete")
        googleC.deleteEvents(deleteCals)
        googleC.createEvents(newCals)

    if config["general"]["provider"] == "caldav":
        deleteCals, newCals = compareEvents(oraribetter, caldav.getEvents(), updatePastEvents)
        print("Found", len(newCals), "new Events and", len(deleteCals), "to delete")
        caldav.deleteEvent(deleteCals)
        caldav.createEvent(newCals)

    if config["general"]["provider"] == "ics":
        saveToIcs(oraribetter)
