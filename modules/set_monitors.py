#!/usr/bin/env python
"""Description.

For current preferred tools see:
https://github.com/WnndGws/boilerplate-repo/blob/python/README.md
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from typing import Any

from loguru import logger

from models.hypr_dataclasses import Display, MonitorAssignment, Profile, Workspace

LAYOUT = "lua:bigbrother"
LAPTOP = "eDP-1"

DISPLAYS = [
    Display(
        output="eDP-1",
        mode="1920x1080@60",
        position="0x0",
        scale=1.0,
        disabled=False,
        transform=0,
    ),
    Display(
        output="DP-4",
        mode="1920x1080@60",
        position="1920x-1080",
        scale=1.0,
        disabled=False,
        transform=2,  # rotate 180
    ),
    Display(
        output="DP-3",
        mode="1920x1080@60",
        position="1920x0",
        scale=1.0,
        disabled=False,
        transform=0,
    ),
    Display(
        output="HDMI-A-2",
        mode="1920x1080@60",
        position="0x-1080",
        scale=1.0,
        disabled=False,
        transform=0,
    ),
]

WORKSPACES = [Workspace(workspace=str(idx)) for idx in range(1, 11)]
WORKSPACES[0].default = True

# Ordered by priority: first match wins.
PROFILES: tuple[Profile, ...] = (
    Profile(
        count=3,
        assignments=(
            MonitorAssignment(0, 2, LAPTOP, LAYOUT, frozenset({"2", "3"})),
            MonitorAssignment(3, 6, "DP-3", LAYOUT, frozenset({"5", "6"}), default="4"),
            MonitorAssignment(
                6,
                None,
                "DP-4",
                LAYOUT,
                frozenset({"8", "9"}),
                default="10",
            ),
        ),
    ),
    Profile(
        count=2,
        required=frozenset({"DP-3"}),
        assignments=(
            MonitorAssignment(0, 4, LAPTOP, LAYOUT),
            MonitorAssignment(5, None, "DP-3", LAYOUT, default="6"),
        ),
    ),
    Profile(
        count=2,
        required=frozenset({"HDMI-A-2"}),
        assignments=(
            MonitorAssignment(0, 4, LAPTOP, LAYOUT),
            MonitorAssignment(6, None, LAPTOP, LAYOUT),
            MonitorAssignment(3, 6, "HDMI-A-2", LAYOUT, default="4"),
        ),
    ),
    Profile(
        count=1,
        assignments=(MonitorAssignment(0, None, None, LAYOUT),),
    ),
)


def _select(count: int, attached: frozenset[str]) -> Profile | None:
    for profile in PROFILES:
        if profile.count == count and profile.required <= attached:
            return profile
    return None


def set_monitors(
    attached_names: Iterable[str],
    send: Callable[[str], str],
    rules: Sequence[Any] = WORKSPACES,
    displays: Sequence[Any] = DISPLAYS,
) -> None:
    attached = frozenset(attached_names)
    profile = _select(len(attached), attached)
    logger.debug(
        "profile: {} monitor(s), {} matched",
        len(attached),
        profile is not None,
    )

    for assignment in profile.assignments if profile else ():
        for rule in rules[assignment.start : assignment.stop]:
            if assignment.monitor is not None:
                rule.monitor = assignment.monitor
            if assignment.layout and (
                not assignment.layout_for or rule.workspace in assignment.layout_for
            ):
                rule.layout = assignment.layout
            if rule.workspace == assignment.default:
                rule.default = True

    for display in displays:
        if display.output not in attached:
            display.disabled = True
        response = send(f"eval hl.monitor({display.stringify()})")
        logger.debug("monitor {}: {}", display.output, response)

    for rule in rules:
        response = send(f"eval hl.workspace_rule({rule.stringify()})")
        logger.debug("workspace {}: {}", rule.workspace, response)


if __name__ == "__main__":
    pass
