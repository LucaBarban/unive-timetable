def compareEvents(newcalendar, oldCalendar):
    deleteCalendar = []
    createCalendar = []

    print("Comparing events...")

    # super simple check, but extremely inefficient (set's would be better)
    for lezione in newcalendar:
        if lezione not in oldCalendar:
            createCalendar.append(lezione)
    for lezione in oldCalendar:
        if lezione not in newcalendar:
            deleteCalendar.append(lezione)
    return deleteCalendar, createCalendar