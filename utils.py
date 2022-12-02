import configparser
import shutil

def check_config():
    print("Checking config file")
    create_config = None
    config = configparser.ConfigParser()
    config.read("config.toml")
    try:
        config['general']['provider']
        print("I've loaded the config file!")
        create_config = False
    except KeyError:
        print("I couldn't find a config file")
        create_config = True

    return create_config

def copy_config(bool):
    status = True
    if bool:
        try:
            shutil.copy("./etc/.toml", "./config.toml")
            print("I craeted a new config in the root of the project")
            status = True
        except FileNotFoundError:
            print("""
                  There's something wrong in your install.
                  Please check a correct at this url:
                  https://github.com/LucaBarban/unive-timetable/blob/main/etc/config.toml
                  """)
            status = False

    return status

def setup_config():
    return copy_config(check_config())
