import re
from datetime import datetime
from typing import List

import requests
from bs4 import BeautifulSoup
from icalendar import Calendar

from unive_timetable.lesson import Lesson

# request the page from the url and scrapre the content via beautifulsoup4
# then lessons that are held in different rooms at the same time will be merged


def shouldIgnore(subject, ignore):
    for x in ignore:
        if re.match(x, subject):
            return True
    return False


def courseCodeToTimetablePage(courseCode: str) -> str:
    urlCourse = f"https://www.unive.it/cdl/{courseCode}"  # main course's page

    soup = BeautifulSoup(
        requests.get(urlCourse).content, "html.parser"
    )  # initialize beautifulsoup

    link = soup.find_all(
        "a",
        class_="list-group-item list-group-item-action",
        string=lambda text: text and "orari" in text,
    )  # get the button that go to the timetable page

    if len(link) != 1:
        raise Exception(
            f"Didn't find the expected number of 'orari' links at {urlCourse} ({len(link)} found)"
        )

    urlRedirect = (
        "https://www.unive.it" + link[0]["href"]
    )  # url that redirects to the timetable page
    urlData = requests.head(urlRedirect, allow_redirects=True)

    return urlData.url


def courseNameToLitteral(courseCode: str, curriculum: str, year: int) -> str:
    url = courseCodeToTimetablePage(courseCode) + "/" + str(year)

    soup = BeautifulSoup(
        requests.get(url).content, "html.parser"
    )  # initialize beautifulsoup

    buttons = soup.find_all(
        "a", class_="btn btn-danger"
    )  # get all the "ics download" buttons

    target_text = f"Genera calendario ICS ({curriculum})"
    ics_url = ""

    for button in buttons:
        if button.text.strip() == target_text:
            ics_url = button.get("href")  # extract the url of the ICS file
            break
    else:
        raise Exception(f'No button "{target_text}" found at url ({url})')

    url_parameters = ics_url.split("?")[1].split("&")  # extract the GET parameters
    for param in url_parameters:  # find the one for the curriculum
        splitted = param.split("=")
        if splitted[0] == "curriculum":
            return splitted[1]

    raise Exception(
        f"Couldn't get the curriculum's litteral from the button's url ({ics_url})"
    )


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


def scrapeLessons(
    courseCode: str, curriculumList: str | list[str], year: int, ignore: List[str]
) -> list[Lesson]:
    lessons: List[Lesson] = []

    if isinstance(curriculumList, str):
        curriculumList = [curriculumList]

    for curriculum in curriculumList:
        if len(curriculum) > 5:  # heuristic based on nothing
            curriculum = courseNameToLitteral(courseCode, curriculum, year)

        ics_url = f"https://www.unive.it/data/ajax/Didattica/generaics?cache=-1&cds={courseCode}&anno={year}&curriculum={curriculum}"
        response = requests.get(ics_url)  # download the ICS file

        if response.status_code == 200:
            calendar = Calendar.from_ical(
                response.text
            )  # parse the downloaded calendar

            # convert each evento into the corresponding lesson
            for event in calendar.walk("vevent"):
                lesson = venevtToLesson(event)
                if shouldIgnore(lesson.getsubject(), ignore):
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
