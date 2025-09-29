from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("signalhire-agent")
except PackageNotFoundError:  # pragma: no cover - during editable installs
    __version__ = "0.0.0"

