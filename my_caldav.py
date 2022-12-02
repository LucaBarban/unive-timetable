from datetime import datetime
from lesson import Lezione

import caldav
import configparser
import keyring


config = configparser.ConfigParser()
config.read("config.toml")

username = config['caldav']['username']
calendar_name = config['general']['calendar']
url = config['caldav']['url']
password = keyring.get_password("Backup Nextcloud", username)

with caldav.DAVClient(url=url, username=username, password=password) as client:
    my_principal = client.principal()

try:
    ## This will raise a NotFoundError if calendar does not exist
    calendar = my_principal.calendar(name=calendar_name)
    assert calendar
except Exception:
    ## If the configured calendar is not found it creates it
    calendar = my_principal.make_calendar(name=calendar_name)

all_events = calendar.events()

def GetEvents():
    events = []
    for event in all_events:
        tuid = event
        event = event.vobject_instance.vevent
        tsummary = event.summary.value
        tactivity = event.description.value.split(" ")[0]
        tday = event.description.value.split(" di ")[1].split("con")[0]
        tclass = event.description.value.split(" in ")[1].split(" di ")[0]
        tlocation = event.location.value
        tprofessor = event.description.value.split(" con ")[1]
        _dtstart = str(event.dtstart.value).split(" ")
        _dtend = str(event.dtend.value).split(" ")
        tdate = _dtstart[0] + "/" + _dtend[0]
        ttime = _dtstart[1] + " - " + _dtend[1]
        events.append(Lezione(tsummary, tday, tdate, tactivity, tprofessor, tlocation, tclass, ttime, tuid))

    return events


def CreateEvent(events):
    for event in events:
        if len(events) > 0:
            calendar.save_event(
                summary=event.getmateria(),
                dtstart=datetime.strptime(event.getStartDateTime(), "%d/%m/%Y-%H:%M"),
                dtend=datetime.strptime(event.getEndDateTime(), "%d/%m/%Y-%H:%M"),
                location=event.getluogo(),
                description=event.getattivita() + " in " + event.getclasse() + " di " + event.getgiorno() + " con " + event.getdocnote(),
                timezone='Europe/Rome',
            )
    print("All events in newCalendars created")

def DeleteEvent(events):
    if len(events) > 0:
        for event in events:
            event.getUID().delete()
