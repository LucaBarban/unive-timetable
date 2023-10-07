import logging as log
import os
from datetime import datetime
from pathlib import Path

from icalendar import Calendar, Event, vText

from unive_timetable.utils import Config


def saveToIcs(calendar, configParser):
    cal = Calendar()

    for lezione in calendar:
        event = Event()
        event.add('summary', lezione.getsubject())
        event.add('description', lezione.getactivity() + " in " + lezione.getclasses() + " di " + lezione.getday() + " con " + lezione.getprof())
        event.add('dtstart', datetime.strptime(
            lezione.getStartDateTime(), "%d/%m/%Y-%H:%M"))
        event.add('dtend', datetime.strptime(
            lezione.getEndDateTime(), "%d/%m/%Y-%H:%M"))

        """
        organizer = vCalAddress("MAILTO:" + lezione.getdocnote() + "@email.domain")

        organizer.params['name'] = vText(lezione.getdocnote())
        organizer.params['role'] = vText('Prof')
        event['organizer'] = organizer
        """

        event['location'] = vText(lezione.getlocation())

        event['uid'] = hash(lezione)
        event.add('priority', 5)

        cal.add_component(event)

    directory = None
    if configParser["ics"]["usepath"] == "true":
        directory = Path.cwd() / configParser["ics"]["folder"]
    else:
        directory = Path(configParser["ics"]["folder"])
    try:
        log.debug(directory)
        directory.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        log.debug("Folder exists")
    else:
        log.debug("Folder created")

    log.info("Saving ics file to disk...")
    f = open(os.path.join(directory, configParser["ics"]["filename"]), 'wb')
    f.write(cal.to_ical())
    f.close()
