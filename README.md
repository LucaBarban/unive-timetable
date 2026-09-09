# unive-timetable

Simple python scraper for unive's timetable.

## Installing

For installing the package itself you can simply clone it on your machine. Or
grab a release zip file.

```bash
# You can git clone
git clone https://github.com/LucaBarban/unive-timetable.git
# Or download the zip file from GitHub
```
## Running the script

```bash
python3 -m unive_timetable
```

## Configuration

The script createas automaticly an **empty** config when you first run it.
Before you run the script again you should populate the config with your info.

# Notes on the data source
If in the past we directly scraped the website, after finding the [open data webpage](https://www.unive.it/pag/13488/) we found out that an official API is provided and [documented here](https://www.unive.it/pag/fileadmin/user_upload/ateneo/mobile/documenti/WebserviceCorsi-Insegnamenti-Orari-Aule-Sedi.pdf). As far as we know, there are no filtering options, which means that the whole timetable for the entire university has to be downloaded. We implemented some caching to make reruns of the script faster.

Technically there is a different API just for the lessons at `http://www.unive.it/data/ajax/Didattica/generaics?afid=xxxxxx` that we could use, but the code is already here and works so... :D And even then, the script can be run at most a few times a month just to check for updates, which means that the bandwidth required from Unive's servers is overall not than much.