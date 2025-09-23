"""Simple logger utility mirroring the legacy Node behaviour."""

from __future__ import annotations

import sys
from typing import Any


class Logger:
    def __init__(self, verbose: bool = True) -> None:
        self.verbose = verbose

    def _print(self, icon: str, message: str, *, stream = sys.stdout) -> None:
        if self.verbose:
            print(f"  {icon} {message}", file=stream)

    def section(self, title: str) -> None:
        if self.verbose:
            print(f"\n{title}")

    def info(self, message: str) -> None:
        self._print("•", message)

    def success(self, message: str) -> None:
        self._print("✅", message)

    def warn(self, message: str) -> None:
        self._print("⚠️", message)

    def error(self, message: str) -> None:
        self._print("❌", message, stream=sys.stderr)

    def debug(self, message: str) -> None:
        self._print("🔍", message)


def create_logger(*, verbose: bool = True) -> Logger:
    return Logger(verbose=verbose)
