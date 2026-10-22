#!/usr/bin/env python
"""Description.

For current preferred tools see:
https://github.com/WnndGws/boilerplate-repo/blob/python/README.md
"""

import time
from pathlib import Path

from loguru import logger
from plumbum import BG, TF, local

CONFIG = Path.home() / ".config/waybar/laptop.json"
WAYBAR = "/usr/bin/waybar"


def _wait_until_gone(name: str, timeout: float = 3.0) -> bool:
    """Keep checking until dead."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not (local["pgrep"]["-x", name] & TF):
            return True
        time.sleep(0.05)
    return False


def restart_waybar() -> None:
    """Kill and restart waybar using config."""
    logger.debug("Restarting waybar with {}", CONFIG)
    matched = (0, 1)  # pkill returns 1 when nothing matched

    local["pkill"]["-x", "waybar"].run(retcode=matched)
    if not _wait_until_gone("waybar"):
        logger.warning("waybar ignored SIGTERM, sending SIGKILL")
        local["pkill"]["-KILL", "-x", "waybar"].run(retcode=matched)

    local[WAYBAR]["-c", str(CONFIG)] & BG


if __name__ == "__main__":
    restart_waybar()
