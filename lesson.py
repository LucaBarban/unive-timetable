class Lezione:
    def __init__(self, subject, day, date, activity, prof, location, classes, time, uid):
        self.subject = subject.strip()  # subject like algebra lineare, programmazione etc
        self.day = day.strip()  # day of the week (Lunedì, Martedì...)
        self.date = date.strip()  # lesson's date (eg. 1/1/2000)
        self.activity = activity.strip()  # activity (lezione/lab?, get a look at the timetable page on the "Attività" coulumn)
        self.prof = prof.strip()  # professor plus some notes (if there are any) on the website, here only the professor's name is saved
        self.location = location.strip()  # where the lesson will be held
        self.classes = classes.strip()  # room where the lesson will be held
        self.time = time.strip() # from what time to what time the lesson will be held
        self.uid = uid # event's uid

    def setDoubleClass(self):
        self.classes = self.classes

    def getsubject(self):
        return self.subject

    def getday(self):
        return self.day

    def getdate(self):
        return self.date

    def getactivity(self):
        return self.activity

    def getprof(self):
        return self.prof

    def getlocation(self):
        return self.location

    def getclasses(self):
        return self.classes

    def gettime(self):
        return self.time

    def getStartDateTime(self):
        return self.date + "-" + self.getStartingTime()

    def getEndDateTime(self):
        return self.date + "-" + self.getEndingingTime()

    def getStartingTime(self):
        return self.time[:self.time.find("-")]

    def getEndingingTime(self):
        return self.time[self.time.find("-"):][1:]

    def getUID(self):
        return self.uid

    def __str__(self):
        return self.date + "," + self.time + "," + self.subject + "," + self.classes + "," + self.prof + "," + self.location + "," + self.activity + "," + self.day

    def __repr__(self):
        return self.date + "," + self.time + "," + self.subject + "," + self.classes + "," + self.prof + "," + self.location + "," + self.activity + "," + self.day

    def __eq__(self, lesson):
        return isinstance(lesson, self.__class__) and self.subject == lesson.subject and self.day == lesson.day and self.date == lesson.date and self.activity == lesson.activity and self.prof == lesson.prof and self.location == lesson.location and self.classes == lesson.classes and self.time == lesson.time

    def __hash__(self):
        tmphash = hash(str(self))
        return tmphash if tmphash >= 0 else tmphash * -1
