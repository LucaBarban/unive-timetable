from datetime import datetime
import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup

from unive_timetable.lesson import Lesson

# request the page from the url and scrapre the content via beautifulsoup4
# then lessons that are held in different rooms at the same time will be merged


def scrapeLessons(url, ignore) -> list[Lesson]:
    timetable = []

    soup = BeautifulSoup(requests.get(url).content, "html.parser")   #initialize beautifulsoup
    periods = soup.select_one("div.tab-content")                     #get the useful contents
    
    nperiods = 0
    for period in periods:
        if period != "\n":                                           #filter out useless stuff
            nperiods += 1

    for periodnumber in range(1, nperiods+1):
        period = soup.find(id=f"collapsep-{periodnumber}").findChild()   #get the card body with all the events
        dontadd = False
        for element in period:
            if element.name == "h5": #if the tag is for a subject
                subject = str(element.findChild().contents).split("\\n\\t")[1].split("\"")[0].split(", <br/>")[0].replace("'", "").strip()   #get the actual title from the link of the subject, split it from the venice/cfu part and clean it up from the formatting
                dontadd = True if subject in ignore else False   #set dontadd to True if the subject has to be ignored, False otherwise
            elif element.name == "div" and not dontadd: #if the tag is for a part of the timetable and it can be added
                collapseid = "collapse"+str(element.get("id"))[6:] #go from giorno-1-1-1 to 1-1-1 to collapse-1-1-1 (the id of the div with the actual entrys from the lessons)
                daydata = element.find_all("div", {"class:", "row"})[0].find_all("div") #get the collapsable row with the day, time, place info
                
                tmphour = "".join(daydata[1].text.split(" ")[1:])   #remove the day from the time part (eg. "Martedì 8:00 - 9:00" becomes "8:00-9:00")
                tmproom = daydata[3].text   #the room where the lessons will be held (eg. Aula 1)
                tmplocation = daydata[4].text   #the building where the romm is
                for entry in soup.find(id=collapseid).find_all("tbody")[0].find_all("tr"):
                    singlelessondata = entry.find_all("td")   #get the data from every table row
                    tmpdate = singlelessondata[0].text
                    tmpactivity = singlelessondata[1].text
                    tmpprof = "".join(singlelessondata[2].text.split(" ")[0:1])   #get the name of the professor (2 words only, the rest is ignored)
                    timetable.append(Lesson(subject, tmpdate, tmpactivity, tmpprof, tmplocation, tmproom, tmphour, 0))   #add the newly "calculated" class
            else: #if it's something else (mainly empty stuff)
                continue

    timetable.sort(key=lambda Lesson: datetime.strptime( Lesson.getStartDateTime(), "%d/%m/%Y-%H:%M")) # sort the lessons (useful for the next step)

    # read all lessons and "merge" the ones that are held in Aula 1 and Aula 2 at the same time, name included (eg. Lesson Classe 1 + Lesson Classe 2 = Lesson Classe 1,2)
    timetablebtr = []
    for lesson in timetable:
        if len(timetablebtr) != 0 and timetablebtr[-1].getStartDateTime() == lesson.getStartDateTime() and timetablebtr[-1].getprof() == lesson.getprof():
            timetablebtr[-1].setDoubleClass()
            tmpSubject = timetablebtr[-1].getsubject().split(" ")
            if len(tmpSubject) > 2 and tmpSubject[-2] in ["Cognomi", "Classe"]:
                tmpNewSubject = " ".join(tmpSubject[:-1])
                tmpNewSubject += " " + tmpSubject[-1] + "," + lesson.getsubject().split(" ")[-1]
                timetablebtr[-1].setSubject(tmpNewSubject)
        else:
            timetablebtr.append(lesson)
    return timetablebtr
        
                                         
            