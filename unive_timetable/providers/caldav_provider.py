import getpass
import logging as log
import sys
from datetime import datetime, timezone

import keyring
from caldav import DAVClient, error
from types import MappingProxyType
from typing import List, Any

from unive_timetable.lesson import Lesson
from unive_timetable.provider import Provider


class CalDAV(Provider):
    def __init__(self, config: MappingProxyType[str, Any]):
        calendar_name = config["general"]["calendar"]
        url = config["caldav"]["url"]
        provider = config["caldav"]["provider"]

        username = config.get("caldav", {}).get("username")
        if username is None:
            username = keyring.get_password(
                "unive_timetable_username_" + provider, "username"
            )
        if username is None:
            username = input("Enter your username for your caldav server: ")
            keyring.set_password(
                "unive_timetable_username_" + provider, "username", username
            )
            username = keyring.get_password(
                "unive_timetable_username_" + provider, "username"
            )

        password = keyring.get_password(
            "unive_timetable_password_" + provider, username
        )
        if password is None:
            pswd = getpass.getpass("Enter your password for your caldav server: ")
            keyring.set_password("unive_timetable_password_" + provider, username, pswd)
            password = keyring.get_password("unive_timetable_" + provider, username)

        with DAVClient(url=url, username=username, password=password) as client:
            my_principal = client.principal()

        try:
            # This will raise a NotFoundError if calendar does not exist
            self.calendar = my_principal.calendar(name=calendar_name)
            assert self.calendar
        except error.NotFoundError:
            # If the configured calendar is not found it creates it
            log.info(f"Making calendar: {calendar_name}")
            self.calendar = my_principal.make_calendar(name=calendar_name)
            log.info("Rerun and make shoure the calendar has been created")
            sys.exit(-1)

        self.all_events = self.calendar.events()

    def getEvents(self) -> List[Lesson]:
        events = []
        for event in self.all_events:
            tuid = event
            event = event.vobject_instance.vevent
            tsummary = event.summary.value
            tactivity = event.description.value.split(" in ")[0]
            tclass = event.description.value.split(" in ")[1].split(" con ")[0]
            tlocation = event.location.value
            tprofessor = event.description.value.split(" con ")[1]
            # Represent date in localtimezone format sinze by default CalDAV will
            # output a datetime object in UTC timezone
            _dtstart = event.dtstart.value.replace(tzinfo=timezone.utc).astimezone(
                tz=None
            )
            _dtend = event.dtend.value.replace(tzinfo=timezone.utc).astimezone(tz=None)
            tdate = str(_dtstart.strftime("%d/%m/%Y"))
            ttime = (
                str(_dtstart.strftime("%H:%M")) + "-" + str(_dtend.strftime("%H:%M"))
            )
            events.append(
                Lesson(
                    tsummary,
                    tdate,
                    tactivity,
                    tprofessor,
                    tlocation,
                    tclass,
                    ttime,
                    tuid,
                )
            )

        return events

    def createEvents(self, events: List[Lesson]):
        for event in events:
            self.calendar.save_event(
                summary=event.getsubject(),
                dtstart=datetime.strptime(event.getStartDateTime(), "%d/%m/%Y-%H:%M"),
                dtend=datetime.strptime(event.getEndDateTime(), "%d/%m/%Y-%H:%M"),
                location=event.getlocation(),
                description=event.getactivity()
                + " in "
                + event.getclasses()
                + " con "
                + event.getprof(),
            )
        log.info("All events in newCalendars created")

    def deleteEvents(self, events: List[Lesson]):
        if len(events) > 0:
            for event in events:
                event.getUID().delete()
