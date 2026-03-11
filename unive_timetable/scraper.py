# Scraper based of the mobile app API. The API is described here:
# https://www.unive.it/pag/fileadmin/user_upload/ateneo/mobile/documenti/WebserviceCorsi-Insegnamenti-Orari-Aule-Sedi.pdf

import json
import re
import unive_timetable.config as cfg
import urllib.request
import logging as log

from datetime import datetime
from pathlib import Path
from typing import List, Dict
from unive_timetable.lesson import Lesson


def shouldIgnore(subject):
    config = cfg.get()
    blacklist = config["general"]["blacklist"]
    whitelist = config["general"]["whitelist"]

    if whitelist:
        for x in whitelist:
            if re.match(x, subject):
                return False
        return True
    else:
        for x in blacklist:
            if re.match(x, subject):
                return True
        return False


def downloadTable(name, output):
    base_url = "https://apps.unive.it/sitows/didattica"
    url = f"{base_url}/{name}"
    chunk_size = 1024 * 1024 # 1MB

    with urllib.request.urlopen(url) as response, open(output, "wb") as f:
        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            f.write(chunk)

    log.info(f"Downloaded API data for '{name}'")


def getAPISchema():
    schema = {}
    cache_dir = Path(".cache")

    if not cache_dir.exists():
        cache_dir.mkdir(parents=True)
        gitignore = cache_dir / ".gitignore"
        gitignore.write_text("*")

    tables = [
        "corsiinsegnamenti",
        "insegnamenti",
        "lezioni",
        "aule",
        "sedi",
    ]

    for table in tables:
        output_file = cache_dir / f"{table}.json"

        if output_file.exists():
            file_mtime = datetime.fromtimestamp(output_file.stat().st_mtime)
            if file_mtime.date() < datetime.today().date():
                downloadTable(table, output_file)
            else:
                log.info(f"Using cached API data for '{table}'")
        else:
            downloadTable(table, output_file)

        with open(output_file, "r") as f:
            schema[table] = json.load(f)

    return schema


def scrapeLessons(courseCode: str) -> List[Lesson]:
    lessons: List[Lesson] = []
    config = cfg.get()

    schema = getAPISchema()

    # Get all 'insegnamenti' for a given code (e.g. CTR3)
    corsiInsegnamentiMap = {}
    for corso in schema["corsiinsegnamenti"]:
        if corso["CDS_COD"] == courseCode:
            corsiInsegnamentiMap[corso["AF_ID"]] = corso

    # Make a map of sedi by their id
    sediMap = {}
    for sede in schema["sedi"]:
        sediMap[sede["SEDE_ID"]] = sede

    auleMap = {}
    for aula in schema["aule"]:
        auleMap[aula["AULA_ID"]] = aula

    # Map every 'insegnamento' to it's argument ID
    insegnamentiLezioniMap = {}
    for insegnamento in schema["insegnamenti"]:
        if shouldIgnore(insegnamento["NOME"]):
            continue
        insegnamentiLezioniMap[insegnamento["AR_ID"]] = insegnamento

    for lezione in schema["lezioni"]:
        insegnamento = insegnamentiLezioniMap.get(lezione["AR_ID"], None)
        if not insegnamento:
            continue

        aula = auleMap[lezione["AULA_ID"]]
        sede = sediMap[aula["SEDE_ID"]]

        subject = insegnamento["NOME"]
        # Date is formatted like YYYY-MM-dd
        _date = lezione["GIORNO"].split("-")
        # We want dd-MM-YYYY
        date = f"{_date[2]}/{_date[1]}/{_date[0]}"
        activity = lezione["TIPO_ATTIVITA"]
        prof = lezione["DOCENTI"].title()
        location = sede["NOME"]
        classes = aula["NOME"]
        time = f"{lezione["INIZIO"]}-{lezione["FINE"]}"

        lessons.append(
            Lesson(
                subject,
                date,
                activity,
                prof,
                location,
                classes,
                time,
                0,
            )
        )

    return cleanupLessons(lessons)


def cleanupLessons(lessons: List[Lesson]):
    lessons.sort(
        key=lambda Lesson: datetime.strptime(
            Lesson.getStartDateTime(), "%d/%m/%Y-%H:%M"
        )
    )  # sort the lessons (useful for the next step)

    # read all lessons and "merge" the ones that are held in Aula 1 and Aula 2 at the same time, name included (eg. Lesson Classe 1 + Lesson Classe 2 = Lesson Classe 1,2)
    lessonsbtr: List[Lesson] = []
    for lesson in lessons:
        if (
            len(lessonsbtr) != 0
            and lessonsbtr[-1].getStartDateTime() == lesson.getStartDateTime()
            and lessonsbtr[-1].getprof() == lesson.getprof()
        ):
            if lessonsbtr[-1].getclasses() in [
                "Aula 1",
                "Aula 2",
            ] and lesson.getclasses() in ["Aula 1", "Aula 2"]:
                lessonsbtr[-1].setDoubleClass()
                tmpSubject = lessonsbtr[-1].getsubject().split(" ")
                if len(tmpSubject) > 2 and tmpSubject[-2] in ["Cognomi", "Classe"]:
                    tmpNewSubject = " ".join(tmpSubject[:-1])
                    tmpNewSubject += (
                        " " + tmpSubject[-1] + "," + lesson.getsubject().split(" ")[-1]
                    )
                    lessonsbtr[-1].setSubject(tmpNewSubject)
        else:
            lessonsbtr.append(lesson)
    return lessonsbtr
