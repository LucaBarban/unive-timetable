#from lesson import Lezione
from lessonScraper import scrapeLessons
from calendarToIcs import saveToIcs
from googleCalendar import GoogleCalendar
from compareEvents import compareEvents
import configparser

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
    print(config['general']['provider'])


saveToIcs(oraribetter, 'CalendariFoscari', 'calendario.ics')
saveToIcs(oraribetter, '', 'calendario.ics')
