import logging as log
import os
import shutil
from datetime import datetime
from os.path import expanduser

import toml

from unive_timetable.lesson import Lesson

"""
super simple check, but extremely inefficient (set's would be better)

the date check works using this truth table
PastDate  UpdatePast  Do It!
0         0           1
0         1           1
1         0           0   # we do not want to update anything in this case
1         1           1
"""


def compareEvents(newcalendar, oldCalendar, updatePastEvents):
    deleteCalendar = []
    createCalendar = []

    now = datetime.now()

    if not updatePastEvents:
        log.info("Comparing future events...")
    else:
        log.info("Comparing all events...")

    for less in newcalendar:
        if less not in oldCalendar and not (
            datetime.strptime(less.getStartDateTime(), "%d/%m/%Y-%H:%M") < now
            and not updatePastEvents
        ):
            createCalendar.append(less)
    for less in oldCalendar:
        if less not in newcalendar and not (
            datetime.strptime(less.getStartDateTime(), "%d/%m/%Y-%H:%M") < now
            and not updatePastEvents
        ):
            deleteCalendar.append(less)
    return deleteCalendar, createCalendar


class Config:
    def __init__(self):
        log.debug("Checking config file")
        home = expanduser("~")
        xdg_conf = os.getenv("XDG_CONFIG_HOME", home + "/.config")
        conf_paths = [
            xdg_conf + "/unive-timetable.toml",
            home + "/.unive-timetable.toml",
        ]
        for path in conf_paths:
            if os.path.exists(path):
                self.path = path
                break
        else:
            self.generate(conf_paths[1])

        with open(self.path, encoding="UTF-8") as f:
            self.data = toml.load(f)

    def generate(self, path):
        try:
            shutil.copy("./etc/config.toml", path)
            log.info(f"I craeted a new config under: {path}")
        except FileNotFoundError:
            log.info(
                "There's something wrong in your install.\n",
                "Please check a correct at this url:\n",
                "https://github.com/LucaBarban/unive-timetable/blob/main/etc/config.toml\n",
            )
        exit()

    def getData(self):
        return self.data
