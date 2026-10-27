from setuptools import setup, find_packages
from pathlib import Path


def get_requirements():
    path = Path("requirements.txt")
    requirements = []
    for line in path.read_text().splitlines():
        if "#" not in line and line.strip():
            requirements.append(line.strip())
    return requirements


setup(
    name="unive_timetable",
    version="0.1.0",
    packages=find_packages(),
    install_requires=get_requirements(),
    entry_points={
        "console_scripts": [
            "unive_timetable=unive_timetable.__main__:main",
        ],
    },
)
