#!/usr/bin/env -S uv run --script
## Run this script using uv
## init uv with `uv init && uv venv && source .venv/bin/activate`
## Check `skeletons/tools/py` for a list of currently preferred tools

# import alive-progress
# import configparser
# import pathlib
import os
import subprocess
import sys

from hyprpy import Hyprland
from hyprpy.utils.shell import run_or_fail
from hyprpy.utils.signals import Signal

# import arrow
# import fastapi
# import httpx
# import humanise
# import joblib
# import maturin
# import orjson
# import plumbum
# import polars
# import pydantic
# import pyright
# import pyspy
# import pytest
# import questionary
# import regex
# import schedule
# import tenacity
# import thefuzz
# import typer
from loguru import logger
from rich.logging import RichHandler

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
                rich_tracebacks=True, show_path=True, tracebacks_show_locals=True
            ),
            "level": "DEBUG",
        }
    ]
)

attached_monitors = instance.get_monitors()
logger.debug(f"Attached monitors: {attached_monitors}")


def set_monitors() -> None:
    # set the monitors when/if they are attached
    if len(attached_monitors) == 3:
        logger.debug("3 Monitors connected")
        logger.debug("Setting laptop monitors")
        response = instance.command_socket.send_command(
            "keyword monitor",
            # name, size, position, scale
            args=["eDP-1,1920x1080@60,-1920x0,1"],
        )
        logger.debug(response)
        response = instance.command_socket.send_command(
            "keyword monitor",
            # name, size, position, scale
            args=["DP-3,1920x1080@60,0x0,1"],
        )
        logger.debug(response)
        response = instance.command_socket.send_command(
            "keyword monitor",
            # name, size, position, scale
            args=["DP-4,1920x1080@60,0x-1080,1"],
        )
        logger.debug(response)

        # Put workspaces on displays
        for space in [1, 2, 3]:
            response = instance.command_socket.send_command(
                "keyword workspace",
                args=[f"{space}, monitor:eDP-1, persistent:true"],
            )
            logger.debug(response)

        for space in [4, 5, 6, 7]:
            response = instance.command_socket.send_command(
                "keyword workspace",
                args=[f"{space}, monitor:DP-3, persistent:true"],
            )
            logger.debug(response)

        logger.debug(response)
        for space in [8, 9, 10]:
            response = instance.command_socket.send_command(
                "keyword workspace",
                args=[f"{space}, monitor:DP-4, persistent:true"],
            )
            logger.debug(response)

    elif len(attached_monitors) == 1:
        logger.debug("1 Monitors connected")
        logger.debug("Setting laptop monitors")
        response = instance.command_socket.send_command(
            "keyword monitor",
            # name, size, position, scale
            args=["eDP-1,1920x1080@60,-1920x0,1"],
        )
        logger.debug(response)

        # Put workspaces on displays
        response = instance.command_socket.send_command(
            "keyword workspace",
            args=["1, monitor:eDP-1, default:true"],
        )
        logger.debug(response)
        for space in [2, 3, 4, 5, 6, 7, 8, 9, 10]:
            response = instance.command_socket.send_command(
                "keyword workspace",
                args=[f"{space}, monitor:eDP-1, persistent:true"],
            )
            logger.debug(response)

    logger.debug(instance.get_workspaces())


def set_waybar():
    logger.debug("Starting waybar")
    with open(os.devnull, "w") as fp:
        subprocess.Popen(
            "killall -9 waybar; sleep 1 && waybar -c /home/wynand/.config/waybar/laptop.json",
            shell=True,
            stdout=fp,
        )


# Define a callback function
def set_monitor_and_waybar(sender, **kwargs):
    logger.debug("Monitors changed")
    set_monitors()
    set_waybar()


if __name__ == "__main__":
    set_monitors()
    set_waybar()

"""
    # Connect the callback function to the signal
    instance.signals.monitoradded.connect(set_monitor_and_waybar)
    instance.signals.monitorremoved.connect(set_monitor_and_waybar)

    # Start watching for hyprland events (is a locking event)
    logger.debug("watching")
    instance.watch()
"""
