import logging as log
import os
import pickle
from datetime import datetime

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from unive_timetable.lesson import Lesson
from unive_timetable.utils import Config

# the implementaton is some sort of a remix from (conmments included :P):
# https://karenapp.io/articles/how-to-automate-google-calendar-with-python-using-the-calendar-api/
# https://developers.google.com/calendar/api


class GoogleCalendar:
    service = None
    config = None

    def __init__(self, CREDENTIALS_FILE, configParser):
        # If modifying these scopes, delete the file token.pickle.
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        creds = None
        self.config = configParser

        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.

        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('calendar', 'v3', credentials=creds)

    def getCalendarId(self, calendarName):
        calendars_result = self.service.calendarList().list().execute()
        calendars = calendars_result.get('items', [])
        log.info("Retriving calendar's events...")

        if not calendars:
            print('No calendars found!')
        for calendar in calendars:
            summary = calendar['summary']
            id = calendar['id']
            if summary == calendarName:
                return id
        print("The given calendar name hasn't been found! ({s})".format(s=calendarName))
        exit()

    def getFromGoogleCalendar(self) -> list[Lesson]:
        gCalendar = []
        id = self.getCalendarId(self.config['general']['calendar'])  # "Orari Uni" is the name of the calendar on gcalendar (will get moved to a config file)
        events = self.service.events().list(calendarId=id, pageToken=None).execute()  # (should) get the first event in the specified calendar

        eventsNumber = 0
        if not events:
            print('Error retriving events (none returned!)')
        else:
            while (True):
                for event in events["items"]:
                    try:
                        tmpAttività = event["description"].split(" in ")[0]
                        tmpClasse = event["description"].split(" in ")[1].split(" di ")[0].split(" con ")[0]
                        tmpDocnote = event["description"].split(" con ")[1]

                        tmpDataPieces = event["start"]["dateTime"].split("T")[0].split("-")
                        tmpData = tmpDataPieces[2] + "/" + tmpDataPieces[1] + "/" + tmpDataPieces[0]

                        tmpTimeList = event["start"]["dateTime"].split("T")[1].split(":")
                        tmpTime = tmpTimeList[0] + ":" + tmpTimeList[1] + "-"
                        tmpTimeList = event["end"]["dateTime"].split("T")[1].split(":")
                        tmpTime += tmpTimeList[0] + ":" + tmpTimeList[1]
                        tmpLocation = "" if "location" not in event else event["location"]
                        gCalendar.append(Lesson(event["summary"], tmpData, tmpAttività, tmpDocnote, tmpLocation, tmpClasse, tmpTime, event["id"]))
                    except Exception as e:
                        log.error(f"Error reading from google calendar on: {event}\nException: {e}")
                        exit()
                eventsNumber += len(events["items"])

                # if len(events["items"]) == 0 or not events["nextPageToken"]:
                if "nextPageToken" not in events or not events["nextPageToken"]:  # if there are no more events, stop iterating
                    break
                events = self.service.events().list(calendarId=id, pageToken=events["nextPageToken"]).execute()  # save the next events form gcalendar to parse them
            log.info(f"{eventsNumber} events on google calendar found")
            return gCalendar

    def deleteEvents(self, calendar):
        if len(calendar) > 0:
            id = self.getCalendarId("Orari Uni")
            log.info("Starting the deletion of removed/modified events")
            for event in calendar:
                try:
                    self.service.events().delete(
                        calendarId=id,
                        eventId=event.getUID(),
                    ).execute()
                except Exception as e:
                    log.error(f"Failed to delete event: {event}\nExeption: {e}")
                    exit()
            log.info("Events in oldCalendar deleted")

    def createEvents(self, calendar):
        if len(calendar) > 0:
            id = self.getCalendarId("Orari Uni")
            log.info("Starting the creation of new events")
            for less in calendar:
                eventBody = {
                    'id': hash(less),
                    'summary': less.getsubject(),
                    'location': less.getlocation(),
                    'description': less.getactivity() + " in " + less.getclasses() + " con " + less.getprof(),
                    'start': {
                        'dateTime': str(datetime.strptime(less.getStartDateTime(), "%d/%m/%Y-%H:%M").isoformat()),
                        'timeZone': 'Europe/Rome',
                    },
                    'end': {
                        'dateTime': str(datetime.strptime(less.getEndDateTime(), "%d/%m/%Y-%H:%M").isoformat()),
                        'timeZone': 'Europe/Rome',
                    }
                }
                self.service.events().insert(calendarId=id, body=eventBody).execute()
            log.info("All events in newCalendars created")
