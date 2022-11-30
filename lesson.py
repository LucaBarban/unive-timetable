class Lezione:
    def __init__(self, materia, giorno, data, attivita, docnote, luogo, classe, orario):
        self.materia = materia.strip()  # subject like algebra lineare, programmazione etc
        self.giorno = giorno.strip()  # day of the week (Lunedì, Martedì...)
        self.data = data.strip()  # lesson's date (eg. 1/1/2000)
        self.attivita = attivita.strip()  # activity (lezione/lab?, get a look at the timetable page on the "Attività" coulumn)
        self.docnote = docnote.strip()  # professor plus some notes (if there are any) on the website, here only the professor's name is saved
        self.luogo = luogo.strip()  # where the lesson will be held
        self.classe = classe.strip()  # room where the lesson will be held
        tmp = orario.strip().split(" - ")
        # from what time to what time the lesson will be held
        self.orario = tmp[0] + "-" + tmp[1]
        self.googleId = "" # event's uid used by gcalendar

    def setDoubleClass(self):
        self.classe = "Aula 1 e 2"

    def getmateria(self):
        return self.materia

    def getgiorno(self):
        return self.giorno

    def getdata(self):
        return self.data

    def getattivita(self):
        return self.attivita

    def getdocnote(self):
        return self.docnote

    def getluogo(self):
        return self.luogo

    def getclasse(self):
        return self.classe

    def getorario(self):
        return self.orario

    def getStartDateTime(self):
        return self.data + "-" + self.getStartingTime()

    def getEndDateTime(self):
        return self.data + "-" + self.getEndingingTime()

    def getDate(self):
        return self.data

    def getTime(self):
        return self.orario

    def getStartingTime(self):
        return self.orario[:self.orario.find("-")]

    def getEndingingTime(self):
        return self.orario[self.orario.find("-"):][1:]

    def setGoogleId(self, id):
        self.googleId = id
    
    def getGoogleId(self):
        return self.googleId

    def __str__(self):
        return self.data + "," + self.orario + "," + self.materia + "," + self.classe + "," + self.docnote + "," + self.luogo + "," + self.attivita + "," + self.giorno

    def __repr__(self):
        return self.data + "," + self.orario + "," + self.materia + "," + self.classe + "," + self.docnote + "," + self.luogo + "," + self.attivita + "," + self.giorno

    def __eq__(self, lesson):
        return isinstance(lesson, self.__class__) and self.materia == lesson.materia and self.giorno == lesson.giorno and self.data == lesson.data and self.attivita == lesson.attivita and self.docnote == lesson.docnote and self.luogo == lesson.luogo and self.classe == lesson.classe and self.orario == lesson.orario

    def __hash__(self):
        tmphash = hash(str(self))
        return tmphash if tmphash >= 0 else tmphash * -1
