#from lesson import Lezione
import configparser

from lessonScraper import scrapeLessons
from googleCalendar import GoogleCalendar
from compareEvents import compareEvents
import my_caldav
import utils

if utils.setup_config():
    config = configparser.ConfigParser()
    config.read("config.toml")
    url = "https://www.unive.it/data/46/" + config['general']['year'] #url to scrape from

    oraribetter = scrapeLessons(url)
    print(str(len(oraribetter)) + " events found")

    if config['general']['provider'] == 'gcal':
        CREDENTIALS_FILE = config['gcal']['credentials']
        googleC = GoogleCalendar(CREDENTIALS_FILE)
        deleteCalendars, newCalendars = compareEvents(oraribetter, googleC.getFromGoogleCalendar())
        print("Found", len(newCalendars), "new Events and", len(deleteCalendars), "to delete")
        googleC.deleteEvents(deleteCalendars)
        googleC.createEvents(newCalendars)

    if config['general']['provider'] == 'caldav':
        deleteCalendars, newCalendars = compareEvents(oraribetter, my_caldav.GetEvents())
        print("Found", len(newCalendars), "new Events and", len(deleteCalendars), "to delete")
        my_caldav.DeleteEvent(deleteCalendars)
        my_caldav.CreateEvent(newCalendars)
