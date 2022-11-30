import os
from pathlib import Path
from icalendar import Calendar, Event, vCalAddress, vText
from datetime import datetime

def saveToIcs(calendar, folder, filename):
    cal = Calendar()

    for lezione in calendar:
        event = Event()
        event.add('summary', lezione.getmateria())
        event.add('description', lezione.getattivita() + " in " +
                lezione.getclasse() + " di " + lezione.getgiorno() + " con " + lezione.getdocnote())
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

        event['location'] = vText(lezione.getluogo())

        event['uid'] = hash(lezione)
        event.add('priority', 5)

        cal.add_component(event)

    directory = Path.cwd() / folder
    try:
        directory.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print("Folder exists")
    else:
        print("Folder created")

    print("Saving ics file to disk...")
    f = open(os.path.join(directory, filename), 'wb')
    f.write(cal.to_ical())
    f.close()
