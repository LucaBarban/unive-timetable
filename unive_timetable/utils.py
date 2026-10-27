import logging as log
import unive_timetable.config as cfg
from datetime import datetime

"""
super simple check, but extremely inefficient (set's would be better)

the date check works using this truth table
PastDate  UpdatePast  Do It!
0         0           1
0         1           1
1         0           0   # we do not want to update anything in this case
1         1           1
"""


def compareEvents(newcalendar, oldCalendar):
    deleteCalendar = []
    createCalendar = []

    now = datetime.now()

    updatePastEvents = cfg.get()["general"]["updatePastEvents"]

    if not updatePastEvents:
        log.info("Comparing future events...")
    else:
        log.info("Comparing all events...")

    for less in newcalendar:
        if less not in oldCalendar and not (
            datetime.strptime(less.getStartDateTime(), "%d/%m/%Y-%H:%M") < now
            and not updatePastEvents
        ):
            createCalendar.append(less)
    for less in oldCalendar:
        if less not in newcalendar and not (
            datetime.strptime(less.getStartDateTime(), "%d/%m/%Y-%H:%M") < now
            and not updatePastEvents
        ):
            deleteCalendar.append(less)
    return deleteCalendar, createCalendar
