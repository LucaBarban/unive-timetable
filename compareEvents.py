from datetime import datetime
from obj_lesson import Lezione

def compareEvents(newcalendar, oldCalendar, updatePastEvents):
    deleteCalendar = []
    createCalendar = []

    now = datetime.now()

    if not updatePastEvents:
        print("Comparing future events...")
    else:
        print("Comparing all events...")

    # super simple check, but extremely inefficient (set's would be better)
    for less in newcalendar:
        # print("NEW CALENDAR")
        # print(less)
        # print("###############")
        if less not in oldCalendar and ((datetime.strptime(less.getStartDateTime()) < now and updatePastEvents) or not updatePastEvents):
            createCalendar.append(less)
    for less in oldCalendar:
        # print("OLD CALENDAR")
        # print(less)
        # print("###############")
        if less not in newcalendar and ((datetime.strptime(less.getStartDateTime()) < now and updatePastEvents) or not updatePastEvents):
            deleteCalendar.append(less)
    return deleteCalendar, createCalendar
