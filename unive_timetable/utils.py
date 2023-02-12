import shutil
import os
import toml
from os.path import expanduser
from datetime import datetime
from unive_timetable.lesson import Lesson

def compareEvents(newcalendar, oldCalendar, updatePastEvents):
    deleteCalendar = []
    createCalendar = []

    now = datetime.now()

    if updatePastEvents:
        print("Comparing future events...")
    else:
        print("Comparing all events...")

    # super simple check, but extremely inefficient (set's would be better)
    for less in newcalendar:
        if less not in oldCalendar and ((datetime.strptime(less.getStartDateTime()) < now and updatePastEvents) or not updatePastEvents):
            createCalendar.append(less)
    for less in oldCalendar:
        if less not in newcalendar and ((datetime.strptime(less.getStartDateTime()) < now and updatePastEvents) or not updatePastEvents):
            deleteCalendar.append(less)
    return deleteCalendar, createCalendar

class Config:
    def __init__(self):
        print("Checking config file")
        home = expanduser("~")
        xdg_conf = os.getenv("XDG_CONFIG_HOME", home + "/.config" )
        conf_paths = [
            xdg_conf + "/unive-timetable.toml",
            home + "/.unive-timetable.toml"
        ]
        for path in conf_paths:
            if os.path.exists(path):
                self.path = path
                break
        else:
            self.generate(conf_paths[0])

        with open(self.path) as f:
            self.data = toml.load(f)

    def generate(self, path):
        try:
            shutil.copy("./etc/config.toml", path)
            print("I craeted a new config in the root of the project")
        except FileNotFoundError:
            print("There's something wrong in your install.\n",
                  "Please check a correct at this url:\n",
                  "https://github.com/LucaBarban/unive-timetable/blob/main/etc/config.toml\n")
        exit()

    def getData(self):
        return self.data
