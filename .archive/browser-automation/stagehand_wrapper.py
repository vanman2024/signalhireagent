"""
Python wrapper for Stagehand browser automation via Node.js bridge.

This module provides a Python interface to Stagehand by launching a Node.js
process and communicating with it via stdin/stdout JSON messages.
"""

import json
import logging
import subprocess
from contextlib import suppress
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class StagehandBridgeError(Exception):
    """Custom exception for Stagehand bridge errors."""


class StagehandBridge:
    """
    Python wrapper for Stagehand browser automation.
    This class launches a Node.js process running the Stagehand bridge
    and communicates with it via JSON messages over stdin/stdout.
    """

    def __init__(self):
        self.process: subprocess.Popen | None = None
        self.is_ready = False

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def start(self) -> None:
        """Start the Node.js bridge process."""
        try:
            # Get path to the bridge script
            bridge_script = Path(__file__).parent / "stagehand_bridge.js"

            if not bridge_script.exists():
                raise StagehandBridgeError(f"Bridge script not found: {bridge_script}")

            # Start the Node.js process
            self.process = subprocess.Popen(
                ["node", str(bridge_script)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            # Wait for ready signal
            ready_response = await self._read_response()
            if not ready_response.get("success") or not ready_response.get("result", {}).get("ready"):
                raise StagehandBridgeError("Bridge failed to start properly")

            self.is_ready = True
            logger.info("Stagehand bridge started successfully")

        except Exception as e:
            if self.process:
                self.process.terminate()
                self.process = None
            raise StagehandBridgeError(f"Failed to start Stagehand bridge: {e}") from e

    async def _send_command(self, action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Send a command to the Node.js bridge and return the response."""
        if not self.process or not self.is_ready:
            raise StagehandBridgeError("Bridge not started")

        command = {"action": action}
        if params:
            command["params"] = params

        try:
            # Send command
            command_json = json.dumps(command) + "\n"
            self.process.stdin.write(command_json)
            self.process.stdin.flush()

            # Read response
            response = await self._read_response()

            if not response.get("success"):
                error_msg = response.get("error", "Unknown error")
                raise StagehandBridgeError(f"Bridge command failed: {error_msg}")

            return response.get("result", {})

        except Exception as e:
            if isinstance(e, StagehandBridgeError):
                raise
            raise StagehandBridgeError(f"Communication error: {e}") from e

    async def _read_response(self) -> dict[str, Any]:
        """Read a JSON response from the Node.js bridge."""
        if not self.process:
            raise StagehandBridgeError("No process to read from")

        try:
            # Read line from stdout
            line = self.process.stdout.readline()
            if not line:
                raise StagehandBridgeError("Bridge process ended unexpectedly")

            return json.loads(line.strip())

        except json.JSONDecodeError as e:
            raise StagehandBridgeError(f"Invalid JSON response: {e}") from e
        except Exception as e:
            raise StagehandBridgeError(f"Failed to read response: {e}") from e

    async def init(self, options: dict[str, Any] | None = None) -> dict[str, Any]:
        """Initialize the browser with optional configuration."""
        return await self._send_command("init", options)

    async def goto(self, url: str) -> dict[str, Any]:
        """Navigate to a URL."""
        return await self._send_command("goto", {"url": url})

    async def act(self, instruction: str, text: str | None = None) -> dict[str, Any]:
        """Perform an action using AI-powered automation."""
        params = {"instruction": instruction}
        if text is not None:
            params["text"] = text
        return await self._send_command("act", params)

    async def observe(self, instruction: str) -> dict[str, Any]:
        """Observe the page state and return information."""
        return await self._send_command("observe", {"instruction": instruction})

    async def wait_for_load_state(self, state: str = "networkidle") -> dict[str, Any]:
        """Wait for the page to reach a specific load state."""
        return await self._send_command("waitForLoadState", {"state": state})

    async def wait_for_url(self, pattern: str, timeout: int = 30000) -> dict[str, Any]:
        """Wait for the URL to match a pattern."""
        return await self._send_command("waitForURL", {"pattern": pattern, "timeout": timeout})

    async def url(self) -> str:
        """Get the current page URL."""
        result = await self._send_command("url")
        return result.get("url", "")

    async def screenshot(self, path: str) -> dict[str, Any]:
        """Take a screenshot and save it to the specified path."""
        return await self._send_command("screenshot", {"path": path})

    async def close(self) -> None:
        """Close the browser and terminate the bridge process."""
        if self.process and self.is_ready:
            with suppress(Exception):  # Ignore errors during shutdown
                await self._send_command("close")

        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except Exception:  # noqa: BLE001
                with suppress(Exception):
                    self.process.kill()
            finally:
                self.process = None
                self.is_ready = False


def check_stagehand_availability() -> bool:
    """Check if Stagehand is available by testing Node.js and package installation."""
    try:
        # Check if Node.js is available
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=True
        )

        # Check if Stagehand package is installed
        result = subprocess.run(
            ["node", "-e", "require('@browserbasehq/stagehand'); console.log('ok')"],
            capture_output=True,
            text=True,
            timeout=5,
            check=True
        )
        return "ok" in result.stdout

    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False
