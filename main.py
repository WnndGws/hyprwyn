#!/usr/bin/env -S uv run --script
## Run this script using uv
## init uv with `uv init && uv venv && source .venv/bin/activate`
## Check `skeletons/tools/py` for a list of currently preferred tools

import sys

from hyprpy import Hyprland
from loguru import logger
from rich.logging import RichHandler

from modules import set_monitors, set_waybar

# Setup hyprland instance
INSTANCE = Hyprland()

# Setup logger with RichHandler for better output
logger.remove()
logger.add(
    sys.stderr,
)
logger.configure(
    handlers=[
        {
            "sink": RichHandler(
                rich_tracebacks=True,
                show_path=True,
                tracebacks_show_locals=True,
            ),
            "level": "DEBUG",
        },
    ],
)

ATTACHED_MONITORS = INSTANCE.get_monitors()
ATTACHED_MONITORS_NAMES = [_m.name for _m in ATTACHED_MONITORS]
logger.debug(f"Attached monitors: {ATTACHED_MONITORS}")
logger.debug(f"Attached monitors: {ATTACHED_MONITORS_NAMES}")


# Define a callback function
def set_monitor_and_waybar(sender, **kwargs) -> None:
    logger.debug("Monitors changed")
    set_monitors.set_monitors(
        attached_names=ATTACHED_MONITORS_NAMES,
        send=INSTANCE.command_socket.send_command,
    )
    set_waybar.restart_waybar()


if __name__ == "__main__":
    set_monitors.set_monitors(
        attached_names=ATTACHED_MONITORS_NAMES,
        send=INSTANCE.command_socket.send_command,
    )

    set_waybar.restart_waybar()

    # Connect the callback function to the signal
    INSTANCE.signals.monitoradded.connect(set_monitor_and_waybar)
    INSTANCE.signals.monitorremoved.connect(set_monitor_and_waybar)

    # Start watching for hyprland events (is a locking event)
    logger.debug("watching")
    INSTANCE.watch()
