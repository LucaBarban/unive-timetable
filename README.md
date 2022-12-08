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
For installing the dependencies you can use either nix or pip.
```bash 
pip install -U -r requirements.txt
# or
nix develop 
```

## Running the script

```bash
python3 run.py
# or
nix develop -c python3 run.py
```

## Configuration

The script createas automaticly an **empty** config when you first run
it. Before you run the script again you should populate the config with your
info.
