from datetime import datetime
import xml.etree.ElementTree as ET
import requests

from lesson import Lezione

# if you think that i remenber how all of this works, then you are wrong :)
# anyway, the code requests the page from the url, conferts it to and xml-tree and scrapres the content.
# as a final step lessons that are held in Aula 1 and Aula 2 at the same time will be merged

def scrapeLessons(url) -> list[Lezione]:
    response = requests.get(url).text
    response = response[response.find(
        "<div class=\"card-body\">"):response.find("<!-- fine col 9-->")]
    response = "<bs>"+response[23:-300]+"</bs>"

    # some debug stuff
    """
    with open('testpagina.html', 'w') as file:
        file.write(response)
    """
    
    """
    with open('testpagina.txt', 'w') as file:
        for lezione in oraribetter:
            print(lezione)
            file.write(str(lezione) + ";\n")
    """

    tree = ET.ElementTree(ET.fromstring(response))
    # ET.dump(tree)

    orari = []
    materia = ""
    giorno = ""
    data = ""
    attivita = ""
    docnote = ""
    luogo = ""
    classe = ""
    orario = ""

    root = tree.getroot()

    for thing in root:
        if thing.tag == "h5":
            materia = list(thing)[0].text
        elif thing.tag == "div":
            children = list(thing)
            children1 = list(children)[0]
            children2 = list(children)[1]

            children1 = list(children1)[0]

            giorno = list(children1)[1].text
            tmp = list(children1)[1]
            orario = tmp[0].text
            tmp = list(children1)[2]
            annotazioni = tmp[0].text
            tmp = list(children1)[3]
            classe = tmp[0].text
            luogo = list(children1)[4].text
            children = list(children1)[1].text

            #print(materia + ", " + giorno + ", " + orario + ", " + classe + ", " + luogo)

            children2 = list(children2)[0]
            children2 = list(children2)[0]
            children2 = list(children2)[0]
            tbody = list(children2)[1]
            for entry in tbody:
                # print(entry.attrib)
                tmp = list(entry)
                data = tmp[0].text
                #print("annotazione:", annotazioni)
                attivita = annotazioni.title() if annotazioni is not None else tmp[1].text
                #print(attivita)
                docnote = tmp[2].text.title()
                if len(list(tmp[2])) > 0: #stupid case where things are writte into an em tag
                    #print(list(tmp[2])[0].text.title())
                    orari.append(Lezione(materia, giorno, data, list(tmp[2])[0].text.title(), 
                                docnote, luogo, classe, orario))
                else:
                    orari.append(Lezione(materia, giorno, data, attivita, 
                                docnote, luogo, classe, orario))
                #print(orari, "\nl")
        else:
            print("rip")
            exit()

    # sort the lessons (useful for the next step)
    orari.sort(key=lambda Lezione: datetime.strptime(
        Lezione.getStartDateTime(), "%d/%m/%Y-%H:%M"))

    # read all lessons and "merge" the ones that are held in Aula 1 and Aula 2 at the same time
    oraribetter = []
    for lezione in orari:
        if len(oraribetter) != 0 and oraribetter[-1].getStartDateTime() == lezione.getStartDateTime():
            oraribetter[-1].setDoubleClass()
        else:
            oraribetter.append(lezione)
    return oraribetter