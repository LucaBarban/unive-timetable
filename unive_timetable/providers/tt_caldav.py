import caldav
import keyring
import getpass

from datetime import datetime
from unive_timetable.lesson import Lesson
from unive_timetable.utils import Config


class CalDAV:
    def __init__(self):
        config = Config().getData()
        username = config["caldav"]["username"]
        calendar_name = config["general"]["calendar"]
        url = config["caldav"]["url"]
        provider = config["caldav"]["provider"]
        password = keyring.get_password("unive_timetable_" + provider, username)
        if password == None:
            pswd = getpass.getpass('Enter your password for your caldav server: ')
            password = keyring.set_password("unive_timetable_" + provider, username, pswd)
            password = keyring.get_password("unive_timetable_" + provider, username)

        with caldav.DAVClient(url=url, username=username, password=password) as client:
            my_principal = client.principal()

        try:
            # This will raise a NotFoundError if calendar does not exist
            self.calendar = my_principal.calendar(name=calendar_name)
            assert self.calendar
        except NotFoundError:
            # If the configured calendar is not found it creates it
            print("Making calendar: " + calendar_name)
            self.calendar = my_principal.make_calendar(name=calendar_name)

        self.all_events = self.calendar.events()



    def getEvents(self) -> list[Lesson]:
        events = []
        for event in self.all_events:
            tuid = event
            event = event.vobject_instance.vevent
            tsummary = event.summary.value
            tactivity = event.description.value.split(" in ")[0]
            tday = event.description.value.split(" di ")[1].split("con")[0]
            tclass = event.description.value.split(" in ")[1].split(" di ")[0]
            tlocation = event.location.value
            tprofessor = event.description.value.split(" con ")[1]
            _dtstart = event.dtstart.value
            _dtend = event.dtend.value
            tdate = str(_dtstart.strftime("%d/%m/%Y"))
            ttime = str(_dtstart.strftime("%H:%M")) + "-" + str(_dtend.strftime("%H:%M"))
            events.append(Lesson(tsummary, tday, tdate, tactivity, tprofessor, tlocation, tclass, ttime, tuid,))

        return events


    def createEvent(self, events):
        for event in events:
            if len(events) > 0:
                self.calendar.save_event(
                    summary=event.getsubject(),
                    dtstart=datetime.strptime(event.getStartDateTime(), "%d/%m/%Y-%H:%M"),
                    dtend=datetime.strptime(event.getEndDateTime(), "%d/%m/%Y-%H:%M"),
                    location=event.getlocation(),
                    description=event.getactivity() + " in " + event.getclasses() + " di " + event.getday() + " con " + event.getprof(),
                    timezone="Europe/Rome",
                )
        print("All events in newCalendars created")


    def deleteEvent(self, events):
        if len(events) > 0:
            for event in events:
                event.getUID().delete()
