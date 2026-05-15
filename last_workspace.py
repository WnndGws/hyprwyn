#!/usr/bin/env python
"""#!/usr/bin/env -S uv run --script
## Run this script using uv
## init uv with `uv init && uv venv && source .venv/bin/activate`
## Check `skeletons/tools/py` for a list of currently preferred tools
"""

from hyprpy import Hyprland
from rich import print

# Setup hyprland instance
instance = Hyprland()


def on_workspace_changed(sender, **kwargs):
    # Retrieve the newly active workspace from the signal's data
    print(sender.__repr__)
    print(kwargs)


instance.signals.workspace.connect(on_workspace_changed)
instance.watch()
