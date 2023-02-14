from datetime import datetime
import xml.etree.ElementTree as ET
import requests

from unive_timetable.lesson import Lesson

# if you think that i remenber how all of this works, then you are wrong :)
# anyway, the code requests the page from the url, conferts it to and xml-tree and scrapres the content.
# as a final step lessons that are held in Aula 1 and Aula 2 at the same time will be merged


def scrapeLessons(url, ignore) -> list[Lesson]:
    response = requests.get(url).text
    response = response[response.find(
        "<div class=\"tab-content\">"):response.find("<!-- fine col 9-->")]
    response = response[0:-7]

    # with open('testpagina.html', 'w') as file:
    #     file.write(response)

    sections = []

    for i in range(1, 5):
        tmpStart = "<div class=\"card tit-no-border espansione\" id=\"periodo-" + str(i) + "\">"
        tmpFinish = "<div class=\"card tit-no-border espansione\" id=\"periodo-" + str(i + 1) + "\">"
        if tmpStart in response:
            tmpSection = response[response.find(tmpStart):response.find(tmpFinish)]
            if i == 1:
                sections.append("<bs>" + tmpSection[tmpSection.find("<div class=\"card-body\">") + 23:-259] + "</bs>")
            else:
                sections.append("<bs>" + tmpSection[tmpSection.find("<div class=\"card-body\">") + 23:-282] + "</bs>")

            # with open('testpagina.html', 'w') as file:
            #     if i == 1:
            #         file.write("<bs>" + tmpSection[tmpSection.find("<div class=\"card-body\">")+23:-259] + "</bs>")
            #     else:
            #         file.write("<bs>" + tmpSection[tmpSection.find("<div class=\"card-body\">")+23:-282] + "</bs>")

    # """
    # with open('testpagina.txt', 'w') as file:
    #     for lezione in oraribetter:
    #         print(lezione)
    #         file.write(str(lezione) + ";\n")
    # """

    orari = []
    subject = ""
    day = ""
    date = ""
    attivita = ""
    prof = ""
    location = ""
    classes = ""
    time = ""

    print("Found", len(sections), "sections on", url)

    for section in sections:
        tree = ET.ElementTree(ET.fromstring(section))
        # ET.dump(tree)

        root = tree.getroot()

        for thing in root:
            if thing.tag == "h5":
                subject = list(thing)[0].text
                subject = str(subject).strip()
            elif thing.tag == "div":
                if subject in ignore:
                    continue
                children = list(thing)
                children1 = list(children)[0]
                children2 = list(children)[1]

                children1 = list(children1)[0]

                day = list(children1)[1].text
                tmp = list(children1)[1]
                tmporario = str(tmp[0].text).split(" - ")
                time = tmporario[0] + "-" + tmporario[1]
                tmp = list(children1)[2]
                annotations = tmp[0].text
                tmp = list(children1)[3]
                classes = tmp[0].text
                location = list(children1)[4].text
                if (location is None):
                    location = ""
                children = list(children1)[1].text

                # print(subject + ", " + day + ", " + time + ", " + classes + ", " + location)

                children2 = list(children2)[0]
                children2 = list(children2)[0]
                children2 = list(children2)[0]
                tbody = list(children2)[1]
                for entry in tbody:
                    # print(entry.attrib)
                    tmp = list(entry)
                    date = tmp[0].text
                    # print("annotazione:", annotazioni)
                    attivita = annotations.title() if annotations is not None else tmp[1].text
                    # print(attivita)
                    # print(subject)
                    prof = tmp[2].text.title()
                    if len(list(tmp[2])) > 0:  # stupid case where things are writte into an em tag
                        # print(list(tmp[2])[0].text.title())
                        try:
                            orari.append(Lesson(subject, day, date, list(tmp[2])[0].text.title(), prof, location, classes, time, 0))
                        except Exception as e:
                            print("Died scraping:", e)
                            print(subject, day, date, tmp[2].text.title(), prof, location, classes, time, 0)

                    else:
                        orari.append(Lesson(subject, day, date, attivita, prof, location, classes, time, 0))
                    # print(orari, "\nl")
            else:
                print("rip")
                exit()

    # sort the lessons (useful for the next step)
    orari.sort(key=lambda Lesson: datetime.strptime(
        Lesson.getStartDateTime(), "%d/%m/%Y-%H:%M"))

    # read all lessons and "merge" the ones that are held in Aula 1 and Aula 2 at the same time, name included (eg. Lesson Classe 1 + Lesson Classe 2 = Lesson Classe 1,2)
    oraribetter = []
    for lezione in orari:
        if len(oraribetter) != 0 and oraribetter[-1].getStartDateTime() == lezione.getStartDateTime() and oraribetter[-1].getprof() == lezione.getprof():
            oraribetter[-1].setDoubleClass()
            tmpSubject = oraribetter[-1].getsubject().split(" ")
            if len(tmpSubject) > 2 and tmpSubject[-2] in ["Cognomi", "Classe"]:
                tmpNewSubject = " ".join(tmpSubject[:-1])
                tmpNewSubject += " " + tmpSubject[-1] + "," + lezione.getsubject().split(" ")[-1]
                oraribetter[-1].setSubject(tmpNewSubject)

        else:
            oraribetter.append(lezione)
    return oraribetter
