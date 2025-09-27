"""Agent context updater (Python port).

This module replaces the legacy Node implementation. It refreshes the
Markdown files that describe each agent so they stay aligned with the local
project's tech stack and recent activity.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Dict, Optional


class AgentContextUpdater:
    """Update agent context Markdown files for the current project."""

    def __init__(self, project_root: Optional[Path] = None, logger=print) -> None:
        self.project_root = Path(project_root or Path.cwd()).resolve()
        self.logger = logger
        self.agents_dir = self.project_root / "agents"
        self.claude_commands_dir = self.project_root / ".claude" / "commands"

    # ------------------------------------------------------------------ helpers
    def extract_project_details(self) -> Dict[str, str]:
        """Infer language/framework metadata from package files."""

        language = "Unknown"
        framework = "Unknown"
        project_type = "Unknown"

        package_json = self.project_root / "package.json"
        if package_json.exists():
            try:
                data = json.loads(package_json.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                data = {}

            deps = {}
            deps.update(data.get("dependencies", {}))
            deps.update(data.get("devDependencies", {}))

            if any(key in deps for key in ("next", "@types/react", "react")):
                framework = "Next.js" if "next" in deps else "React"
                language = "TypeScript/JavaScript"
                project_type = "Full-stack Web Application" if "next" in deps else "Frontend Application"
            elif "express" in deps:
                framework = "Express"
                language = "JavaScript/Node.js"
                project_type = "Backend API"
            elif deps:
                framework = "Node.js"
                language = "JavaScript"
                project_type = "Node.js Application"
            return {"language": language, "framework": framework, "projectType": project_type}

        requirements = self.project_root / "requirements.txt"
        pyproject = self.project_root / "pyproject.toml"
        if requirements.exists() or pyproject.exists():
            language = "Python"
            req_content = requirements.read_text(encoding="utf-8") if requirements.exists() else ""
            py_content = pyproject.read_text(encoding="utf-8") if pyproject.exists() else ""
            if "fastapi" in req_content or "fastapi" in py_content:
                framework = "FastAPI"
                project_type = "API Server"
            elif "django" in req_content or "django" in py_content:
                framework = "Django"
                project_type = "Web Application"
            elif "flask" in req_content or "flask" in py_content:
                framework = "Flask"
                project_type = "Web Application"
            else:
                framework = "Python"
                project_type = "Python Application"

        return {"language": language, "framework": framework, "projectType": project_type}

    # ---------------------------------------------------------- individual files
    def update_claude_context(self) -> bool:
        self.logger("🤖 Updating Claude agent context...")
        claude_file = self.agents_dir / "CLAUDE.md"
        if not claude_file.exists():
            self.logger("⚠️  Claude context file not found, skipping")
            return False

        details = self.extract_project_details()
        content = claude_file.read_text(encoding="utf-8")

        pattern = re.compile(r"### Current Project Context[\s\S]*?(?=\n###|\Z)")
        replacement = (
            "### Current Project Context\n"
            f"- **Language**: {details['language']}\n"
            f"- **Framework**: {details['framework']}\n"
            f"- **Project Type**: {details['projectType']}\n"
            "- **Coordination**: @Symbol task assignment system\n"
            "- **MCP Servers**: Local filesystem, git, github, memory, sequential-thinking,"
            " playwright, sqlite, supabase, postman\n\n"
        )

        if pattern.search(content):
            claude_file.write_text(pattern.sub(replacement, content), encoding="utf-8")
            self.logger("✅ Updated Claude context with current project details")
            return True

        self.logger("⚠️  Could not find project context section in Claude file")
        return False

    def update_gemini_context(self) -> bool:
        self.logger("🔍 Updating Gemini agent context...")
        gemini_file = self.agents_dir / "GEMINI.md"
        if not gemini_file.exists():
            self.logger("⚠️  Gemini context file not found, skipping")
            return False

        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-10"],
                cwd=self.project_root,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            topics = [
                re.sub(r"^[0-9a-f]+\s+", "", line)
                for line in result.stdout.splitlines()
                if re.search(r"(feat|fix|docs|refactor|perf):", line)
            ][:5]
        except subprocess.CalledProcessError:
            topics = []

        if not topics:
            return False

        section = (
            "### Current Sprint Focus\n"
            "Based on recent development activity:\n"
            + "\n".join(topics)
            + "\n\n"
        )
        content = gemini_file.read_text(encoding="utf-8")
        pattern = re.compile(r"### Current Sprint Focus[\s\S]*?(?=\n###|\Z)")
        if pattern.search(content):
            gemini_file.write_text(pattern.sub(section, content), encoding="utf-8")
            self.logger("✅ Updated Gemini context with recent development topics")
            return True
        return False

    def update_agents_guidelines(self) -> bool:
        self.logger("📋 Updating repository guidelines...")
        agents_file = self.agents_dir / "README.md"
        if agents_file.exists():
            return False

        templates_dir = Path(__file__).resolve().parent.parent.parent / "templates"
        overview = templates_dir / "agents_readme.md"
        if overview.exists():
            content = overview.read_text(encoding="utf-8")
        else:
            content = (
                """# Multi-Agent Development Team

## Agent Coordination System

This directory contains context files for each AI agent in our multi-agent development system.

### Updating Agent Context

Agent contexts are automatically updated during project sync and can be manually refreshed using the `multiagent` CLI.
"""
            )
        agents_file.write_text(content, encoding="utf-8")
        self.logger("✅ Created agents overview file")
        return True

    def update_copilot_instructions(self) -> bool:
        self.logger("🛠️  Updating GitHub Copilot instructions...")
        copilot_file = self.project_root / ".github" / "copilot-instructions.md"
        copilot_file.parent.mkdir(parents=True, exist_ok=True)
        if copilot_file.exists():
            self.logger("✅ GitHub Copilot instructions already exist")
            return False

        details = self.extract_project_details()
        templates_dir = Path(__file__).resolve().parent.parent.parent / "templates"
        instructions = templates_dir / "copilot_instructions.md"
        if instructions.exists():
            template = instructions.read_text(encoding="utf-8")
            rendered = template.format(**details)
        else:
            rendered = (
                "# GitHub Copilot Instructions\n\n"
                "## Project Context\n"
                f"- **Type**: {details['projectType']}\n"
                f"- **Language**: {details['language']}  \n"
                f"- **Framework**: {details['framework']}\n"
                "- **Architecture**: Multi-agent development framework template\n"
            )
        copilot_file.write_text(rendered, encoding="utf-8")
        self.logger("✅ Created GitHub Copilot instructions")
        return True

    # ------------------------------------------------------------------- public
    def update_all(self, target: str = "all") -> Dict[str, int]:
        self.logger("🚀 Starting agent context update...")
        self.agents_dir.mkdir(parents=True, exist_ok=True)
        self.claude_commands_dir.mkdir(parents=True, exist_ok=True)

        updated = 0
        if target in ("all", "claude"):
            updated += 1 if self.update_claude_context() else 0
        if target in ("all", "gemini"):
            updated += 1 if self.update_gemini_context() else 0
        if target in ("all", "agents"):
            updated += 1 if self.update_agents_guidelines() else 0
        if target in ("all", "copilot"):
            updated += 1 if self.update_copilot_instructions() else 0

        if updated:
            self.logger(f"✅ Agent context update complete! Updated {updated} context files")
        else:
            self.logger("ℹ️  No context files needed updating")

        return {"success": True, "updated": updated}


def main(target: str = "all", project_root: Optional[Path] = None) -> Dict[str, int]:
    updater = AgentContextUpdater(project_root)
    return updater.update_all(target)


if __name__ == "__main__":  # pragma: no cover
    import argparse

    parser = argparse.ArgumentParser(description="Update agent context files")
    parser.add_argument("target", nargs="?", default="all", help="Specific agent to update")
    args = parser.parse_args()
    main(args.target)
