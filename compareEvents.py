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
    #
    # the date check works using this truth table
    # PastDate  UpdatePast  Do It!
    # 0         0           1
    # 0         1           1
    # 1         0           0   # we do not want to update anything in this case
    # 1         1           1
    
    for less in newcalendar:
        # print("NEW CALENDAR")
        # print(less)
        # print("###############")
        if less not in oldCalendar and not (datetime.strptime(less.getStartDateTime(), "%d/%m/%Y-%H:%M") < now and not updatePastEvents):
            createCalendar.append(less)
    for less in oldCalendar:
        # print("OLD CALENDAR")
        # print(less)
        # print("###############")
        if less not in newcalendar and not (datetime.strptime(less.getStartDateTime(), "%d/%m/%Y-%H:%M") < now and not updatePastEvents):
            deleteCalendar.append(less)
    return deleteCalendar, createCalendar
