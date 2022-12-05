import shutil
import os

def check_config(verbose):
    if verbose:
        print("Checking config file")
    if os.path.exists("./config.toml"):
        if verbose:
            print("I've loaded the config file!")
        return True
    else:
        if verbose:
            print("I couldn't find a config file")
        return False

def copy_config(exists):
    if exists:
        try:
            shutil.copy("./etc/config.toml", "./config.toml")
            print("I craeted a new config in the root of the project")
        except FileNotFoundError:
            print("There's something wrong in your install.\n",
                  "Please check a correct at this url:\n",
                  "https://github.com/LucaBarban/unive-timetable/blob/main/etc/config.toml\n")
    exit()

def load():
    return check_config(False)

def setup_config():
    if check_config(True):
        return True
    copy_config(True)
