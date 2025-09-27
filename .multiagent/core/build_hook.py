#!/usr/bin/env python3
"""Post-build hook to auto-update all deployments."""

import sys
from pathlib import Path

# Add project root to path (from .multiagent/core/ to project root)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from multiagent_core.auto_updater import hook_into_build

if __name__ == "__main__":
    print("\n[BUILD] Build complete, running auto-update hook...")
    hook_into_build()