#from lesson import Lezione
from lessonScraper import scrapeLessons
from calendarToIcs import saveToIcs
from googleCalendar import GoogleCalendar
from compareEvents import compareEvents

url = "https://www.unive.it/data/46/1" #url to scrape from 

CREDENTIALS_FILE = '' #token path (used for google calendar only)

oraribetter = scrapeLessons(url) #scrape stuff from website (returns lists of lessons)
print(str(len(oraribetter)) + " events found")

googleC = GoogleCalendar(CREDENTIALS_FILE) 
deleteCalendars, newCalendars = compareEvents(oraribetter, googleC.getFromGoogleCalendar()) #compare the newly scraped lessons with the ones that are saved on google calendar

print("Found", len(newCalendars), "new Events and", len(deleteCalendars), "to delete")

googleC.deleteEvents(deleteCalendars) #delete events on gcalendar
googleC.createEvents(newCalendars) #create events on gcalendar

#saveToIcs(oraribetter, 'CalendariFoscari', 'calendario.ics') #save lessons to an ics file (current path + CalendariFoscari folder + filename)
saveToIcs(oraribetter, '', 'calendar.ics') 