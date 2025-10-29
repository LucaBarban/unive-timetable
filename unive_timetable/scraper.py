import re
from datetime import datetime
from typing import List, Dict

import unive_timetable.config as cfg
import requests
from bs4 import BeautifulSoup
from icalendar import Calendar

from unive_timetable.lesson import Lesson

# request the page from the url and scrapre the content via beautifulsoup4
# then lessons that are held in different rooms at the same time will be merged


generaICSUrl = "https://www.unive.it/data/ajax/Didattica/generaics?cache=-1"


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


def formatSearchUrl(url: str, parameters: Dict[str, str]) -> str:
    parametersString = "".join(f"&{k}={v}" for k, v in parameters.items())
    return f"{url}?{parametersString}"


def getParsedPage(url: str, post=False):
    """
    Returns the parser for the page and the url in case it did change due to a redirect
    """
    response = (
        requests.get(url, allow_redirects=True)
        if not post
        else requests.post(url, allow_redirects=True)
    )
    if response.status_code != 200:
        raise Exception(f"Failed to get {url} (code: {response.status_code})")
    parser = BeautifulSoup(response.content, "html.parser")
    # if the url didn't change
    return parser, response.url if url != response.url else url


def getLessonsUrls(courseCode: str) -> List[str]:
    lessonUrls: List[str] = []

    ## Generate search url ##

    searchPage, searchPageUrl = getParsedPage(
        "https://www.unive.it/pag/ricercainsegnamenti"
    )

    # find search form
    form = searchPage.find("form", id="form-ricercainsegnamenti")
    if not form:
        raise Exception(f"Didn't find the search form ({searchPageUrl})")

    # search all url parameters in form
    urlParameters = {}
    for node in form.find_all(["input", "select"]):
        if "id" in node.attrs:
            urlParameters[node.attrs["id"]] = ""
    # add other required parameters
    urlParameters["cds"] = courseCode
    urlParameters["cerca"] = "cerca"

    searchUrlWithParams = formatSearchUrl(searchPageUrl, urlParameters)

    ## Get lessons urls ##

    lessonsList, _ = getParsedPage(searchUrlWithParams, post=True)

    table = lessonsList.find("table", class_="table table-hover")
    if not table:
        raise Exception(f"Didn't found lessons table ({searchUrlWithParams})")

    tableBody = table.find("tbody")
    if not tableBody:
        raise Exception(f"Found empty lessons table ({searchUrlWithParams})")

    for row in tableBody.find_all("tr"):
        cells = row.find_all(["td"])
        linkTag = cells[0].find("a")
        if not linkTag:
            continue

        text = linkTag.get_text(strip=True)
        if shouldIgnore(text):
            continue
        href = linkTag.get("href")

        lessonID = href.split("/")[-1]
        lessonUrls.append(f"{generaICSUrl}&afid={lessonID}")

    return lessonUrls


def venevtToLesson(vevent) -> Lesson:
    summary = vevent.get("SUMMARY")

    subject = summary.split(" - ")
    # there is a " - Mod" lesson
    if len(subject) == 3:
        subject = f"{subject[0]} - {subject[1]}"
    else:
        subject = subject[0]

    # format the start date as 'day/month/year'
    date = vevent.get("DTSTART").dt.strftime("%d/%m/%Y")

    # find the activity
    activity = summary[len(subject) + 3 :].split(", ")[1]

    # fin the professor's surname and name
    prof = summary[len(subject) + 3 :].split(", ")[0].title()

    # find time
    start_time = vevent.get("DTSTART").dt.strftime("%H:%M")
    end_time = vevent.get("DTEND").dt.strftime("%H:%M")
    time = f"{start_time}-{end_time}"

    # find location
    location = vevent.get("LOCATION")
    classes = ""
    if location != "ALTRO Altro":
        match = re.search(r"^(.*?)(?=\s+Campus)", location)
        if match is None:
            raise Exception(f"Couldn't parse the location of the room ({location})")
        classes = match.group(1)
        location = location[len(classes) + 1 :]
    else:
        location = ""

    # match everything inside []
    match = re.search(r"\[[^\]]*\]", subject)
    if match is None:
        raise Exception(f"Couldn't parse the course id ({subject})")
    course_id = match.group()

    # take only the subject part without the id (the minus - 1 is for the trailing space)
    subject = subject[: len(subject) - len(course_id) - 1]

    return Lesson(
        subject,
        date,
        activity,
        prof,
        location,
        classes,
        time,
        0,
    )


def scrapeLessons(courseCode: str) -> List[Lesson]:
    lessons: List[Lesson] = []
    ics_urls = getLessonsUrls(courseCode)
    config = cfg.get()

    for lessonID in config["general"].get("injectedLessons", []):
        ics_urls.append(f"{generaICSUrl}&afid={lessonID}")

    for ics_url in ics_urls:
        response = requests.get(ics_url)  # download the ICS file

        if response.status_code == 200:
            # parse the downloaded calendar
            calendar = Calendar.from_ical(response.text)

            # convert each evento into the corresponding lesson
            for event in calendar.walk("vevent"):
                lesson = venevtToLesson(event)
                if shouldIgnore(lesson.getsubject()):
                    continue
                lessons.append(lesson)
        else:
            raise Exception(
                f"Failed to download ICS from {ics_url} (satus: {response.status_code})"
            )

    return cleanupLessons(lessons)


def scrapeLessonsFromCode(lessonCode: List[str]) -> List[Lesson]:
    for ics_url in ics_urls:
        response = requests.get(ics_url)  # download the ICS file

        if response.status_code == 200:
            # parse the downloaded calendar
            calendar = Calendar.from_ical(response.text)

            # convert each evento into the corresponding lesson
            for event in calendar.walk("vevent"):
                lesson = venevtToLesson(event)
                if shouldIgnore(lesson.getsubject()):
                    continue
                lessons.append(lesson)
        else:
            raise Exception(
                f"Failed to download ICS from {ics_url} (satus: {response.status_code})"
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
