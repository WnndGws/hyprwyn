#!/usr/bin/env -S uv run --script
## Run this script using uv
## init uv with `uv init && uv venv && source .venv/bin/activate`
## Check `skeletons/tools/py` for a list of currently preferred tools

import os
import subprocess
import sys

from hyprpy import Hyprland
from loguru import logger
from rich.logging import RichHandler

from models import hypr_dataclasses

# Setup hyprland instance
instance = Hyprland()

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

DISPLAYS = [
    hypr_dataclasses.Display(
        output="eDP-1",
        mode="1920x1080@60",
        position="0x0",
        scale=1.0,
        disabled=False,
        transform=0,
    ),
    hypr_dataclasses.Display(
        output="DP-4",
        mode="1920x1080@60",
        position="1920x-1080",
        scale=1.0,
        disabled=False,
        transform=2,  # rotate 180
    ),
    hypr_dataclasses.Display(
        output="DP-3",
        mode="1920x1080@60",
        position="1920x0",
        scale=1.0,
        disabled=False,
        transform=0,
    ),
    hypr_dataclasses.Display(
        output="HDMI-A-2",
        mode="1920x1080@60",
        position="0x-1080",
        scale=1.0,
        disabled=False,
        transform=0,
    ),
]

WORKSPACES = [hypr_dataclasses.Workspace(workspace=str(idx)) for idx in range(1, 11)]
WORKSPACES[0].default = True

attached_monitors = instance.get_monitors()
attached_monitors_names = [_m.name for _m in attached_monitors]
logger.debug(f"Attached monitors: {attached_monitors}")
logger.debug(f"Attached monitors: {attached_monitors_names}")


def set_monitors() -> None:
    # set the monitors when/if they are attached
    if len(attached_monitors) == 3:
        for ws in WORKSPACES[:2]:
            ws.monitor = "eDP-1"
            if ws.workspace in ["2", "3"]:
                ws.layout = "dwindle"

        for ws in WORKSPACES[3:6]:
            ws.monitor = "DP-3"
            if ws.workspace == "4":
                ws.default = True
            if ws.workspace in ["5", "6"]:
                ws.layout = "dwindle"

        for ws in WORKSPACES[6:]:
            ws.monitor = "DP-4"
            if ws.workspace == "10":
                ws.default = True
            if ws.workspace in ["8", "9"]:
                ws.layout = "dwindle"

    elif len(attached_monitors) == 2:
        logger.trace("HERE 1")
        if "DP-3" in attached_monitors_names:
            for ws in WORKSPACES[:4]:
                ws.monitor = "eDP-1"
                if ws.workspace in ["2", "3", "4"]:
                    ws.layout = "dwindle"

            for ws in WORKSPACES[5:]:
                ws.monitor = "DP-3"
                if ws.workspace == "6":
                    ws.default = True
                if ws.workspace in ["7", "8", "9"]:
                    ws.layout = "dwindle"

        elif "HDMI-A-2" in attached_monitors_names:
            logger.trace("HERE")
            for ws in WORKSPACES[:4]:
                ws.monitor = "eDP-1"
                if ws.workspace in ["2", "3", "4"]:
                    ws.layout = "dwindle"
            for ws in WORKSPACES[6:]:
                ws.monitor = "eDP-1"
            for ws in WORKSPACES[3:6]:
                ws.monitor = "HDMI-A-2"
                if ws.workspace == "4":
                    ws.default = True
                if ws.workspace == "5":
                    ws.layout = "dwindle"

    elif len(attached_monitors) == 1:
        for ws in WORKSPACES:
            if ws.workspace in ["2", "3", "4", "6", "7", "8"]:
                ws.layout = "dwindle"

    logger.debug("Setting laptop monitors")
    for display in DISPLAYS:
        if display.output not in attached_monitors_names:
            display.disabled = True

    for display in DISPLAYS:
        logger.warning(display)
        response = instance.command_socket.send_command(
            f"eval hl.monitor({display.stringify()})",
        )
        logger.debug(response)

    for ws in WORKSPACES:
        response = instance.command_socket.send_command(
            f"eval hl.workspace_rule({ws.stringify()})",
        )
        logger.debug(ws)

    logger.debug(instance.get_workspaces())


def set_waybar() -> None:
    logger.debug("Starting waybar")
    with open(os.devnull, "w") as fp:
        subprocess.Popen(
            "killall -9 waybar; sleep 1 && waybar -c /home/wynand/.config/waybar/laptop.json",
            shell=True,
            stdout=fp,
        )


# Define a callback function
def set_monitor_and_waybar(sender, **kwargs) -> None:
    logger.debug("Monitors changed")
    set_monitors()
    set_waybar()


if __name__ == "__main__":
    set_monitors()
    set_waybar()

    # Connect the callback function to the signal
    instance.signals.monitoradded.connect(set_monitor_and_waybar)
    instance.signals.monitorremoved.connect(set_monitor_and_waybar)

    # Start watching for hyprland events (is a locking event)
    logger.debug("watching")
    instance.watch()
