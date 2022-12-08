import configparser
import mycaldav as caldav
import utils

from scraper import scrapeLessons
from gcal import GoogleCalendar
from compareEvents import compareEvents

if utils.setup_config():
    config = configparser.ConfigParser()
    config.read("config.toml")
    url = "https://www.unive.it/data/46/" + config['general']['year']  # url to scrape from
    ignore = config['general']['ignore']

    oraribetter = scrapeLessons(url, ignore)
    print(str(len(oraribetter)) + " events found")

    if config['general']['provider'] == 'gcal':
        CREDENTIALS_FILE = config['gcal']['credentials']
        googleC = GoogleCalendar(CREDENTIALS_FILE)
        deleteCalendars, newCalendars = compareEvents(oraribetter, googleC.getFromGoogleCalendar())
        print("Found", len(newCalendars), "new Events and", len(deleteCalendars), "to delete")
        googleC.deleteEvents(deleteCalendars)
        googleC.createEvents(newCalendars)

    if config['general']['provider'] == 'caldav':
        deleteCalendars, newCalendars = compareEvents(oraribetter, caldav.getEvents())
        print("Found", len(newCalendars), "new Events and", len(deleteCalendars), "to delete")
        caldav.deleteEvent(deleteCalendars)
        caldav.createEvent(newCalendars)
