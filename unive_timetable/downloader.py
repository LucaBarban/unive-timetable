import requests
import icalendar
import re
from unive_timetable.lesson import Lesson
from pathlib import Path
from typing import Literal, List


def download(curriculum: Literal["DS", "TSI", "ECS"], year: int) -> Path:
    url = f"https://www.unive.it/data/ajax/Didattica/generaics?cache=-1&cds=CT3&anno={year}&curriculum={curriculum}"
    request = requests.get(url, allow_redirects=True)
    dir = Path(".ics")
    # Make sure that the directory is present
    dir.mkdir(exist_ok=True)
    filename = dir / f"{curriculum}_{year}.ics"
    open(filename, "wb").write(request.content)
    return filename


def icsToLesson(vevent) -> Lesson:
    summary = vevent.get("SUMMARY")
    subject = summary.split(" - ")
    # There is a " - Mod" lesson
    if len(subject) == 3:
        subject = f"{subject[0]} - {subject[1]}"
    else:
        subject = subject[0]
    # Format the start date as 'day/month/year'
    date = vevent.get("DTSTART").dt.strftime("%d/%m/%Y")
    activity = summary[len(subject) + 3 :].split(", ")[1]
    prof = summary[len(subject) + 3 :].split(", ")[0]
    # find time
    start_time = vevent.get("DTSTART").dt.strftime("%H:%M")
    end_time = vevent.get("DTEND").dt.strftime("%H:%M")
    time = f"{start_time}-{end_time}"
    # find aula
    location = vevent.get("LOCATION")
    classes = re.search("^(Aula|Laboratorio) \\w+", location).group()
    # Include trailing space in "Aula Laboratorio \w+ blah blah"
    #                                                ^
    location = location[len(classes) + 1 :]
    # Match everything inside []
    course_id = re.search("\\[[^\\]]*\\]", subject).group()
    # Take only the subject part without the id (the minus - 1 is for the trailing space)
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


def getLessons(
    curriculum: Literal["DS", "TSI", "ECS"], year: int, ignore: List[str]
) -> List[Lesson]:
    ics_path = download(curriculum, year)
    with ics_path.open() as f:
        calendar = icalendar.Calendar.from_ical(f.read())

    lessons = []
    for event in calendar.walk("VEVENT"):
        lesson = icsToLesson(event)
        if lesson.getsubject() not in ignore:
            lessons.append(lesson)

    return lessons
