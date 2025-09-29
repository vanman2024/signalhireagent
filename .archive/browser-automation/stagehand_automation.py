"""
Simple Python wrapper for Stagehand automation.

This module provides a clean Python interface to Stagehand by calling
simple Node.js scripts via subprocess.
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class StagehandAutomation:
    """Simple Python interface to Stagehand automation."""

    def __init__(self):
        self.script_path = Path(__file__).parent / "stagehand_runner.js"

    def run_automation(self, action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Run a Stagehand automation action."""
        try:
            cmd = ["node", str(self.script_path), action]
            if params:
                cmd.append(json.dumps(params))

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                check=True
            )

            # Try to parse JSON response
            try:
                return json.loads(result.stdout.strip().split('\n')[-1])
            except json.JSONDecodeError:
                return {"success": True, "output": result.stdout}

        except subprocess.CalledProcessError as e:
            logger.error(f"Automation failed: {e.stderr}")
            raise
        except Exception as e:
            logger.error(f"Automation error: {e}")
            raise

    def test_connection(self) -> bool:
        """Test if Stagehand is working."""
        try:
            result = self.run_automation("test")
            return result.get("success", False)
        except Exception:
            return False

    def login(self, email: str, password: str) -> dict[str, Any]:
        """Login to SignalHire."""
        return self.run_automation("login", {
            "email": email,
            "password": password
        })

    def search_prospects(self, criteria: dict[str, Any]) -> dict[str, Any]:
        """Search for prospects."""
        return self.run_automation("search", criteria)
