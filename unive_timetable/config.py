import logging as log
import os
import pathlib
import shutil
from pathlib import Path
from types import MappingProxyType
from typing import Any, Tuple

import toml  # type: ignore[import-untyped]

config = None


def _gen_config(path: Path):
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


def _load_config() -> MappingProxyType[str, Any]:
    log.debug("Checking config file")
    home = pathlib.Path.home()

    xdg_config: Path

    xdg_config_env: Any = os.getenv("XDG_CONFIG_HOME")
    if xdg_config_env is not None:
        xdg_config = Path(xdg_config_env)
    else:
        xdg_config = home / ".config"

    config_paths: Tuple[Path, Path] = (
        xdg_config / "unive-timetable.toml",
        home / ".unive-timetable.toml",
    )

    config_path: Path = config_paths[1]
    for path in config_paths:
        if path.exists():
            config_path = path
            break
    else:
        _gen_config(config_path)

    with open(config_path, encoding="UTF-8") as f:
        return MappingProxyType(toml.load(f))


def get() -> MappingProxyType[str, Any]:
    global config
    if config is None:
        config = _load_config()
    return config
