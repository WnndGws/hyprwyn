#!/usr/bin/env python
"""#!/usr/bin/env -S uv run --script
## Run this script using uv
## init uv with `uv init && uv venv && source .venv/bin/activate`
## Check `skeletons/tools/py` for a list of currently preferred tools
"""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class MonitorAssignment:
    """Hand a slice of the workspace list to one monitor."""

    start: int
    stop: int | None = None  # None means "to the end"
    monitor: str | None = None  # None leaves ws.monitor untouched
    layout: str | None = None
    layout_for: frozenset[str] = frozenset()  # empty means "every workspace here"
    default: str | None = None


@dataclass(frozen=True)
class Profile:
    """One monitor arrangement. `required` names must all be attached."""

    count: int
    assignments: tuple[MonitorAssignment, ...]
    required: frozenset[str] = frozenset()


@dataclass
class Display:
    """Display property values."""

    output: str = "eDP-1"
    mode: str = "1920x1080@60"
    position: str = "0x0"
    scale: float = 1.0
    disabled: bool = False
    transform: int = 0

    def stringify(self):
        _kv_pairs = [
            f"{k}='{v}'"
            if isinstance(v, str)
            else f"{k}={str(v).lower()}"
            if isinstance(v, bool)
            else f"{k}={v}"
            for k, v in asdict(self).items()
        ]
        return f"{{{', '.join(_kv_pairs)}}}"


@dataclass
class Workspace:
    """Workspace property values."""

    workspace: str = "1"
    default: bool = False
    monitor: str = "eDP-1"
    persistent: bool = True
    on_created_empty: str = "alacritty"
    layout: str = "master"

    def stringify(self):
        _kv_pairs = [
            f"{k}='{v}'"
            if isinstance(v, str)
            else f"{k}={str(v).lower()}"
            if isinstance(v, bool)
            else f"{k}={v}"
            for k, v in asdict(self).items()
        ]
        return f"{{{', '.join(_kv_pairs)}}}"
