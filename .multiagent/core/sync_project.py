#!/usr/bin/env python3
"""Python port of the ProjectSync utility.

This module preserves the behaviour of the original sync-project.js script
while translating its implementation to Python so it can participate in the
unified pip-based toolchain. The public API mirrors the JavaScript class to
avoid breaking existing automation that instantiates ProjectSync or calls its
methods.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from modules.agent_context_updater import AgentContextUpdater
from template_updater import TemplateUpdateSystem
from webhook_notifier import WebhookUpdateNotifier
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

TEMPLATE_ROOT = Path(__file__).resolve().parent.parent
CORE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = TEMPLATE_ROOT / "config" / "project-sync-config.template.json"
TEMPLATES_DIR = TEMPLATE_ROOT / "environments"


class ProjectSync:
    def __init__(self, project_root: Optional[Path] = None) -> None:
        self.projectRoot = Path(project_root or Path.cwd()).resolve()
        self.config = self.loadConfig()
        self.detectedTechStack: Optional[Dict[str, Any]] = None
        self.updateCommands: list[str] = []
        self.args: list[str] = []

    # -- Config -----------------------------------------------------------------
    def loadConfig(self) -> Dict[str, Any]:
        try:
            raw = CONFIG_FILE.read_text(encoding="utf-8")
            return json.loads(raw)
        except Exception as exc:  # broad match to mirror JS behaviour
            print(f"❌ Failed to load project sync config: {exc}", file=sys.stderr)
            raise SystemExit(1) from exc

    # -- Detection --------------------------------------------------------------
    def detectTechStack(self) -> Dict[str, Any]:
        print("🔍 Detecting technology stack...")

        detected = {}
        patterns = self.config.get("techStackDetection", {}).get("patterns", {})
        _ = patterns  # Placeholder to mirror original access; patterns used later.

        if self.fileExists("package.json"):
            package_json = self.readJsonFile("package.json")
            deps = {}
            deps.update(package_json.get("dependencies", {}))
            deps.update(package_json.get("devDependencies", {}))

            if any(key in deps for key in ("react", "next", "@types/react")):
                detected["frontend"] = "react"
                if "next" in deps:
                    detected["framework"] = "nextjs"

        if self.fileExists("requirements.txt") or self.fileExists("pyproject.toml"):
            detected["backend"] = "python"

            req_content = ""
            if self.fileExists("requirements.txt"):
                req_content = (self.projectRoot / "requirements.txt").read_text(encoding="utf-8")
            pyproject_content = ""
            if self.fileExists("pyproject.toml"):
                pyproject_content = (self.projectRoot / "pyproject.toml").read_text(encoding="utf-8")

            if "fastapi" in req_content or "fastapi" in pyproject_content:
                detected["framework"] = "fastapi"
            elif "django" in req_content or "django" in pyproject_content:
                detected["framework"] = "django"
            elif "flask" in req_content or "flask" in pyproject_content:
                detected["framework"] = "flask"

        if self.fileExists("package.json") and "backend" not in detected:
            package_json = self.readJsonFile("package.json")
            deps = {}
            deps.update(package_json.get("dependencies", {}))
            deps.update(package_json.get("devDependencies", {}))

            if any(key in deps for key in ("express", "fastify", "@nestjs/core")):
                detected["backend"] = "node"
                if "express" in deps:
                    detected["framework"] = "express"
                if "fastify" in deps:
                    detected["framework"] = "fastify"
                if "@nestjs/core" in deps:
                    detected["framework"] = "nestjs"

        if detected.get("frontend") and detected.get("backend"):
            detected["type"] = "full-stack"
        elif detected.get("frontend"):
            detected["type"] = "frontend"
        elif detected.get("backend"):
            detected["type"] = "backend"
        else:
            detected["type"] = "unknown"

        self.detectedTechStack = detected
        print(f"✅ Detected tech stack: {detected}")
        return detected

    # -- Sync operations --------------------------------------------------------
    def syncAgentFiles(self) -> None:
        print("👥 Syncing agent files...")

        agent_files = self.config.get("agentFiles", {})
        sync_count = 0

        for agent_file in agent_files.get("required", []):
            source_path, target_path = self._resolve_agent_paths(agent_file)
            if source_path.exists():
                self.ensureDirectoryExists(target_path.parent)
                shutil.copy2(source_path, target_path)

                if agent_file.startswith("scripts/"):
                    try:
                        os.chmod(target_path, 0o755)
                    except OSError as exc:
                        print(f"  ⚠️  Could not make {agent_file} executable: {exc}")

                sync_count += 1
                display_path = (
                    f"agents/{source_path.name}"
                    if agent_file.startswith("template-agents/")
                    else agent_file
                )
                print(f"  ✅ Synced {display_path}")
            else:
                print(f"  ⚠️  Source not found: {agent_file}")

        for agent_file in agent_files.get("optional", []):
            source_path, target_path = self._resolve_agent_paths(agent_file)
            if source_path.exists():
                self.ensureDirectoryExists(target_path.parent)
                shutil.copy2(source_path, target_path)
                sync_count += 1
                display_path = (
                    f"agents/{source_path.name}"
                    if agent_file.startswith("template-agents/")
                    else agent_file
                )
                print(f"  ✅ Synced optional {display_path}")

        for agent_swarm_dir in agent_files.get("agentSwarm", []):
            source_path = Path(__file__).resolve().parent / agent_swarm_dir
            target_path = self.projectRoot / agent_swarm_dir
            if source_path.exists():
                self.copyDirectoryRecursively(source_path, target_path, overwrite=False)
                sync_count += 1
                print(f"  ✅ Synced {agent_swarm_dir} directory")

        print(f"📁 Synced {sync_count} agent files")

        agents_dir = self.projectRoot / "agents"
        self.ensureDirectoryExists(agents_dir)
        print("  📁 Agent files synced to agents/ directory")

    def syncGitHubWorkflows(self) -> None:
        print("⚙️  Syncing GitHub workflows...")

        workflows = self.config.get("githubWorkflows", {}).get("essential", [])
        workflow_count = 0

        for workflow in workflows:
            source_path = Path(__file__).resolve().parent / workflow
            target_path = self.projectRoot / workflow
            if source_path.exists():
                self.ensureDirectoryExists(target_path.parent)
                shutil.copy2(source_path, target_path)
                workflow_count += 1
                print(f"  ✅ Synced {workflow}")
            else:
                print(f"  ⚠️  Workflow not found: {workflow}")

        if workflow_count:
            print(f"🔄 Synced {workflow_count} GitHub workflows")

    def syncGitHubIssueTemplates(self) -> None:
        print("📋 Syncing GitHub issue templates...")

        issue_templates = [
            ".github/ISSUE_TEMPLATE/bug_report.yml",
            ".github/ISSUE_TEMPLATE/feature_request.yml",
            ".github/ISSUE_TEMPLATE/task.yml",
            ".github/ISSUE_TEMPLATE/hotfix.yml",
            ".github/ISSUE_TEMPLATE/config.yml",
        ]

        template_count = 0
        for template in issue_templates:
            source_path = Path(__file__).resolve().parent / template
            target_path = self.projectRoot / template
            if source_path.exists():
                self.ensureDirectoryExists(target_path.parent)
                shutil.copy2(source_path, target_path)
                template_count += 1
                print(f"  ✅ Synced {Path(template).name}")
            else:
                print(f"  ⚠️  Template not found: {template}")

        if template_count:
            print(f"📋 Synced {template_count} issue templates")

    def syncVersioningSystem(self) -> None:
        print("🏷️  Syncing versioning system...")

        versioning_source = Path(__file__).resolve().parent.parent / "templates" / "versioning"
        if not versioning_source.exists():
            print("  ⚠️  Versioning templates not found")
            return

        sync_count = 0

        gitmessage_source = versioning_source / ".gitmessage"
        gitmessage_target = self.projectRoot / ".gitmessage"
        if gitmessage_source.exists():
            if not gitmessage_target.exists():
                shutil.copy2(gitmessage_source, gitmessage_target)
                sync_count += 1
                print("  ✅ Synced .gitmessage template")
            else:
                print("  ℹ️  .gitmessage already exists, skipping")

        try:
            subprocess.run(
                ["git", "config", "commit.template", ".gitmessage"],
                check=True,
                cwd=self.projectRoot,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            print("  ✅ Configured git commit template")
        except subprocess.CalledProcessError as exc:
            print(f"  ⚠️  Could not configure git commit template: {exc.stderr.decode().strip() or exc}")

        version_file = self.projectRoot / "VERSION"
        if not version_file.exists():
            project_name = self.projectRoot.name
            initial_version = {
                "name": project_name,
                "version": "0.1.0",
                "description": f"{project_name} project",
                "last_updated": datetime.utcnow().strftime("%Y-%m-%d"),
                "features": [
                    "semantic-versioning",
                    "conventional-commits",
                    "automated-releases"
                ]
            }
            version_file.write_text(json.dumps(initial_version, indent=2), encoding="utf-8")
            print("  ✅ Created initial VERSION file with modern format")
            sync_count += 1

        if sync_count:
            print("  ✅ Synced {} versioning components".format(sync_count))
            print("  📋 Versioning system configured:")
            print("     • .gitmessage - Conventional commit template with multi-agent signatures")
            print("     • VERSION file - Tracks project version and build metadata")
            print("     • Git commit template configured for conventional commits")
            print("     • Workflow: version-management.yml synced via GitHub workflows")
        else:
            print("  ℹ️  Versioning system already configured")

    def syncMcpConfigurations(self) -> None:
        print("🔧 MCP Server Management...")
        print("  ℹ️  MCP servers are now managed by Claude Code directly")
        print("  ℹ️  Use the /add-mcp slash command to configure servers:")
        print("     • /add-mcp github    - GitHub repository management")
        print("     • /add-mcp vercel    - Deployment and hosting")
        print("     • /add-mcp playwright - Browser automation and testing")
        print("     • /add-mcp memory    - Persistent context storage")
        print("     • /add-mcp all       - Add all essential servers")
        print("  ✅ MCP guidance provided")


    def createTemplateVersionTracking(self) -> None:
        print("🏷️  Setting up template version tracking...")
        try:
            template_version = "unknown"
            version_file = TEMPLATE_ROOT / "VERSION"
            if version_file.exists():
                try:
                    data = json.loads(version_file.read_text(encoding="utf-8"))
                    template_version = data.get("version", "unknown")
                except json.JSONDecodeError:
                    for line in version_file.read_text(encoding="utf-8").splitlines():
                        if line.lower().startswith("version"):
                            template_version = line.split(":", 1)[1].strip()
                            break

            template_version_file = self.projectRoot / ".template-version"
            info = """TEMPLATE_VERSION={template_version}
TEMPLATE_REPO=https://github.com/vanman2024/multi-agent-claude-code
SYNC_DATE={sync_date}

# Template Update Commands:
# multiagent update --check
# multiagent update --preview
# multiagent update
""".format(template_version=template_version, sync_date=datetime.utcnow().date())
            template_version_file.write_text(info, encoding="utf-8")
            print(f"  ✅ Created .template-version ({template_version})")

            setup_dir = self.projectRoot / "setup"
            setup_dir.mkdir(parents=True, exist_ok=True)
            update_script_target = setup_dir / "update_from_template.py"
            source_script = Path(__file__).resolve().parent / "update_from_template.py"
            if source_script.exists():
                shutil.copy2(source_script, update_script_target)
                print("  ✅ Copied Python template update script")
        except Exception as exc:
            print(f"  ⚠️  Failed to set up template version tracking: {exc}")

    def syncVSCodeSettings(self) -> None:
        print("⚙️  Syncing VS Code settings...")

        source_vscode_dir = Path(__file__).resolve().parent / ".vscode"
        target_vscode_dir = self.projectRoot / ".vscode"

        if not source_vscode_dir.exists():
            print("  ⚠️  Source .vscode directory not found")
            return

        self.ensureDirectoryExists(target_vscode_dir)

        source_settings = source_vscode_dir / "settings.json"
        target_settings = target_vscode_dir / "settings.json"

        if source_settings.exists():
            if not target_settings.exists():
                shutil.copy2(source_settings, target_settings)
                print("  ✅ Synced .vscode/settings.json")
            else:
                self.updateVSCodeSettings(source_settings, target_settings)

        for extra_file in source_vscode_dir.iterdir():
            if extra_file.name == "settings.json":
                continue
            target_file = target_vscode_dir / extra_file.name
            if extra_file.is_file() and not target_file.exists():
                shutil.copy2(extra_file, target_file)
                print(f"  ✅ Synced .vscode/{extra_file.name}")

        print("  ✅ Synced VS Code settings")


    def registerForTemplateUpdates(self) -> None:
        print("\n📡 Registering project for template update notifications...")
        notifier = WebhookUpdateNotifier(Path(__file__).resolve().parent / 'deployed-projects-registry.json')
        if not (self.projectRoot / '.git').exists():
            print('  ⚠️  No git repository detected - skipping auto-registration')
            return
        remote_proc = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            cwd=self.projectRoot,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if remote_proc.returncode != 0:
            print('  ⚠️  No GitHub remote detected - skipping auto-registration')
            return
        remote_url = remote_proc.stdout.strip()
        parts = remote_url.split('github.com')[-1].strip('/:').split('/') if 'github.com' in remote_url else []
        if len(parts) < 2:
            print('  ⚠️  Could not parse GitHub remote, skipping registration')
            return
        owner, repo = parts[-2], parts[-1].replace('.git', '')
        template_version = self.getTemplateVersion()
        config = {
            'name': f'{owner}/{repo}',
            'webhook_url': f'https://api.github.com/repos/{owner}/{repo}/dispatches',
            'owner': owner,
            'repo': repo,
            'deployed_version': template_version,
            'critical_updates_only': True,
        }
        notifier.add_project(config)
        print(f"  ✅ Registered {owner}/{repo} for update notifications")
    def updateVSCodeSettings(self, source_settings: Path, target_settings: Path) -> None:
        try:
            source_data = json.loads(source_settings.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"  ⚠️  Could not parse source VS Code settings: {exc}")
            return

        try:
            target_data = json.loads(target_settings.read_text(encoding="utf-8")) if target_settings.exists() else {}
        except json.JSONDecodeError:
            target_data = {}

        updated = False
        critical_updates = {"workbench.iconTheme": "vs-seti"}
        for key, value in critical_updates.items():
            if target_data.get(key) != value:
                target_data[key] = value
                updated = True

        if updated:
            target_settings.write_text(json.dumps(target_data, indent=2), encoding="utf-8")
            print("  🔄 Updated .vscode/settings.json with critical fixes (file icons)")
        else:
            print("  ↪️  .vscode/settings.json already up to date")


    def updateAgentContexts(self) -> None:
        print("🤖 Updating agent contexts...")
        updater = AgentContextUpdater(self.projectRoot)
        result = updater.update_all("all")
        updated = result.get("updated", 0)
        if updated:
            print(f"  ✅ Updated {updated} agent context file(s)")
        else:
            print("  ℹ️  Agent context files already up to date")
    # -- Helpers ----------------------------------------------------------------
    def _resolve_agent_paths(self, agent_file: str) -> tuple[Path, Path]:
        if agent_file.startswith('.github/'):
            source_path = Path(__file__).resolve().parent / agent_file
            target_path = self.projectRoot / agent_file
        elif agent_file.startswith('.multiagent/templates/'):
            source_path = Path(__file__).resolve().parent / agent_file
            target_path = self.projectRoot / 'agents' / Path(agent_file).name
        elif agent_file.startswith('.multiagent/tools/'):
            source_path = Path(__file__).resolve().parent / agent_file
            target_path = self.projectRoot / agent_file
        elif agent_file.startswith('automation/'):
            source_path = Path(__file__).resolve().parent / agent_file
            if agent_file.endswith('.template'):
                target_file = agent_file.replace('.template', '')
                target_path = self.projectRoot / '.automation' / Path(target_file).name
            else:
                target_path = self.projectRoot / '.automation' / Path(agent_file).name
        elif agent_file.startswith('docs/'):
            source_path = Path(__file__).resolve().parent / agent_file
            target_path = self.projectRoot / agent_file
        else:
            source_path = Path(__file__).resolve().parent.parent / agent_file
            target_path = self.projectRoot / agent_file
        return source_path, target_path

    def copyDirectory(self, source: Path, target: Path, overwrite: bool = True) -> None:
        source = Path(source)
        target = Path(target)
        if not source.exists():
            return
        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            for item in source.iterdir():
                self.copyDirectory(item, target / item.name, overwrite)
        else:
            if target.exists() and not overwrite:
                return
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            if os.access(source, os.X_OK):
                try:
                    os.chmod(target, 0o755)
                except OSError:
                    pass

    def updateVSCodeSettingsAlias(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover - compatibility shim
        self.updateVSCodeSettings(*args, **kwargs)

    def fileExists(self, file_path: str) -> bool:
        return (self.projectRoot / file_path).exists()

    def readJsonFile(self, file_path: str) -> Dict[str, Any]:
        try:
            return json.loads((self.projectRoot / file_path).read_text(encoding="utf-8"))
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError as exc:
            print(f"  ⚠️  Could not parse JSON file {file_path}: {exc}")
            return {}

    def ensureDirectoryExists(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)

    def syncProjectEssentials(self) -> None:
        print("📋 Syncing project essentials...")
        env_path = self.projectRoot / '.env'
        if not env_path.exists():
            env_path.write_text('# Environment variables\n', encoding='utf-8')
            print('  ✅ Created .env placeholder')

        gitignore_target = self.projectRoot / '.gitignore'
        gitignore_source = TEMPLATE_ROOT / '.gitignore'
        if gitignore_source.exists() and not gitignore_target.exists():
            shutil.copy2(gitignore_source, gitignore_target)
            print("  ✅ Created .gitignore")

        self.syncProductionReadinessTools()
        self.syncMainScripts()
        self.syncHooks()
        self.syncDocumentation()
        self.updateGitignore()
        self.updatePackageJsonScripts()

    def syncProductionReadinessTools(self) -> None:
        helpers_source = TEMPLATE_ROOT / 'config' / 'helpers'
        helpers_target = self.projectRoot / 'scripts' / 'helpers'
        if not helpers_source.exists():
            return
        helpers_target.mkdir(parents=True, exist_ok=True)
        copied = 0
        for script in helpers_source.iterdir():
            target = helpers_target / script.name
            shutil.copy2(script, target)
            try:
                os.chmod(target, 0o755)
            except OSError:
                pass
            copied += 1
        if copied:
            print(f"  ✅ Synced {copied} production helper scripts")

    def syncHooks(self) -> None:
        hooks_source = TEMPLATE_ROOT / 'core' / '.claude' / 'hooks'
        if not hooks_source.exists():
            return
        hooks_target = self.projectRoot / '.claude' / 'hooks'
        hooks_target.mkdir(parents=True, exist_ok=True)
        for hook in hooks_source.iterdir():
            target = hooks_target / hook.name
            if not target.exists():
                shutil.copy2(hook, target)
                try:
                    os.chmod(target, 0o755)
                except OSError:
                    pass
        print("  ✅ Synced hooks into .claude/hooks")

    def syncDocumentation(self) -> None:
        docs_source = TEMPLATE_ROOT / 'docs'
        if not docs_source.exists():
            return
        docs_target = self.projectRoot / 'docs'
        docs_target.mkdir(parents=True, exist_ok=True)
        copied = 0
        for doc in docs_source.iterdir():
            if doc.is_file():
                shutil.copy2(doc, docs_target / doc.name)
                copied += 1
        if copied:
            print(f"  ✅ Synced {copied} documentation files")

    def updateGitignore(self) -> None:
        gitignore_path = self.projectRoot / '.gitignore'
        additions = self.config.get('projectEssentials', {}).get('gitignoreAdditions', [])
        if not gitignore_path.exists() or not additions:
            return
        current = gitignore_path.read_text(encoding='utf-8')
        new_entries = [entry for entry in additions if entry not in current]
        if new_entries:
            appended = current.rstrip('\n') + '\n' + '\n'.join(new_entries) + '\n'
            gitignore_path.write_text(appended, encoding='utf-8')
            print(f"  ✅ Added {len(new_entries)} entries to .gitignore")

    def updatePackageJsonScripts(self) -> None:
        package_json_path = self.projectRoot / 'package.json'
        if not package_json_path.exists() or not self.detectedTechStack:
            return
        package_json = self.readJsonFile('package.json')
        testing_key = self.getTestingKey(self.detectedTechStack)
        commands = self.config.get('testingStandards', {}).get('commandsByTechStack', {}).get(testing_key)
        if not commands:
            return
        scripts = package_json.setdefault('scripts', {})
        updated = False
        for name, command in commands.items():
            if name not in scripts:
                scripts[name] = command
                updated = True
        if updated:
            package_json_path.write_text(json.dumps(package_json, indent=2), encoding='utf-8')
            print('  ✅ Added testing scripts to package.json')

    def getTestingKey(self, tech_stack: Dict[str, Any]) -> str:
        if tech_stack.get('frontend') == 'react' and tech_stack.get('framework') == 'nextjs':
            return 'react-nextjs'
        if tech_stack.get('backend') == 'python' and tech_stack.get('framework') == 'fastapi':
            return 'python-fastapi'
        if tech_stack.get('backend') == 'python' and tech_stack.get('framework') == 'django':
            return 'python-django'
        if tech_stack.get('backend') == 'node' and tech_stack.get('framework') == 'express':
            return 'node-express'
        return 'python-fastapi'

    def syncMainScripts(self) -> None:
        source_project = TEMPLATE_ROOT / 'project'
        source_docker = TEMPLATE_ROOT / 'docker'
        target_scripts = self.projectRoot / 'scripts'
        copied = 0
        if source_docker.exists():
            docker_script = source_docker / 'docker-scripts.sh'
            if docker_script.exists():
                dest = self.projectRoot / 'docker-scripts.sh'
                if not dest.exists():
                    shutil.copy2(docker_script, dest)
                    try:
                        os.chmod(dest, 0o755)
                    except OSError:
                        pass
                    copied += 1
            sync_docker = source_docker / 'sync-docker.js'
            if sync_docker.exists():
                target_scripts.mkdir(parents=True, exist_ok=True)
                dest = target_scripts / 'sync-docker.js'
                if not dest.exists():
                    shutil.copy2(sync_docker, dest)
                    try:
                        os.chmod(dest, 0o755)
                    except OSError:
                        pass
                    copied += 1
        if source_project.exists():
            helpers_source = source_project / 'helpers'
            helpers_target = target_scripts / 'helpers'
            if helpers_source.exists():
                self.copyDirectory(helpers_source, helpers_target, overwrite=True)
                for helper in helpers_target.glob('*.sh'):
                    try:
                        os.chmod(helper, 0o755)
                    except OSError:
                        pass
                copied += 1
        if copied:
            print(f"  ✅ Synced {copied} project scripts")

    def syncTestingStructure(self) -> None:
        print('🧪 Syncing testing structure...')
        tests_root = TEMPLATE_ROOT / 'tests'
        if not tests_root.exists():
            print('  ⚠️  Testing templates not found')
            return
        skip_backend = '--frontend-only' in self.args or '--no-testing' in self.args
        skip_frontend = '--backend-only' in self.args or '--no-testing' in self.args
        package_json_path = self.projectRoot / 'package.json'
        pyproject_path = self.projectRoot / 'pyproject.toml'
        requirements_path = self.projectRoot / 'requirements.txt'
        is_python = pyproject_path.exists() or requirements_path.exists()
        is_node = package_json_path.exists()
        sync_count = 0
        if not skip_backend:
            backend_source = tests_root / 'backend'
            if backend_source.exists():
                self.copyDirectory(backend_source, self.projectRoot / 'tests' / 'backend', overwrite=True)
                sync_count += 1
        if not skip_frontend:
            frontend_source = tests_root / 'frontend'
            if frontend_source.exists():
                self.copyDirectory(frontend_source, self.projectRoot / 'tests' / 'frontend', overwrite=True)
                sync_count += 1
        if sync_count:
            print(f"  ✅ Synced {sync_count} testing suites")
        elif '--no-testing' in self.args:
            print('  ⏭️  Testing setup skipped (--no-testing)')
        else:
            print('  ⚠️  No testing structure copied (templates missing or flags)')

    def syncDevOpsSystem(self) -> None:
        print('🔧 Syncing DevOps system...')
        devops_source = TEMPLATE_ROOT / 'devops'
        devops_target = self.projectRoot / 'devops'
        if not devops_source.exists():
            print('  ⚠️  DevOps source directory not found')
            return
        self.copyDirectory(devops_source, devops_target, overwrite=True)
        for script in [devops_target / 'ops' / 'ops', devops_target / 'deploy' / 'deploy']:
            if script.exists():
                try:
                    os.chmod(script, 0o755)
                except OSError:
                    pass
        print('  ✅ DevOps system files synced')

    def runDevOpsSetup(self) -> None:
        print("\n🔧 Setting up DevOps system...")
        ops_script = self.projectRoot / 'devops' / 'ops' / 'ops'
        if not ops_script.exists():
            print('  ⚠️  DevOps scripts not found, skipping setup')
            return
        try:
            subprocess.run([str(ops_script), 'setup'], check=True, cwd=self.projectRoot)
            print('  ✅ DevOps system initialized')
        except subprocess.CalledProcessError as exc:
            print(f"  ⚠️  DevOps setup completed with warnings: {exc}")

    def syncClaudeDirectory(self) -> None:
        print("🤖 Syncing .claude directory...")
        source_claude = TEMPLATE_ROOT / '.claude'
        target_claude = self.projectRoot / '.claude'
        if not source_claude.exists():
            print('  ⚠️  Source .claude directory not found')
            return
        self.copyDirectory(source_claude, target_claude, overwrite=False)
        global_settings_path = Path.home() / '.claude' / 'settings.json'
        target_settings_path = target_claude / 'settings.json'
        source_settings_path = source_claude / 'settings.json'
        try:
            settings = {}
            if source_settings_path.exists():
                settings = json.loads(source_settings_path.read_text(encoding='utf-8'))
            hooks = settings.get('hooks')
            if isinstance(hooks, dict):
                for hook_groups in hooks.values():
                    for hook_group in hook_groups:
                        for hook in hook_group.get('hooks', []):
                            command = hook.get('command')
                            if hook.get('type') == 'command' and command and '.claude/hooks/' in command:
                                tokens = command.split()
                                prefix = tokens[0] if tokens else 'bash'
                                script_name = command.split('.claude/hooks/')[-1]
                                hook['command'] = f"{prefix} {target_claude / 'hooks' / script_name}"
                print('  ✅ Converted hook paths to absolute for current project')
            if global_settings_path.exists():
                global_settings = json.loads(global_settings_path.read_text(encoding='utf-8'))
                if 'permissions' in global_settings:
                    settings['permissions'] = global_settings['permissions']
                if 'mcpServers' in global_settings:
                    settings['mcpServers'] = global_settings['mcpServers']
            target_settings_path.write_text(json.dumps(settings, indent=2), encoding='utf-8')
            print('  ✅ Merged Claude settings (project hooks + global permissions)')
        except Exception as exc:
            print(f"  ⚠️  Could not merge Claude settings: {exc}")
            if source_settings_path.exists():
                shutil.copy2(source_settings_path, target_settings_path)
        for subdir in ('hooks', 'scripts'):
            dir_path = target_claude / subdir
            if dir_path.exists():
                for item in dir_path.iterdir():
                    if item.suffix in {'.sh', '.py'}:
                        try:
                            os.chmod(item, 0o755)
                        except OSError:
                            pass
        print('  ✅ Synced complete .claude directory with commands, agents, and hooks')

    def syncDockerTemplates(self) -> None:
        print('🐳 Syncing Docker development environment...')
        source_docker = TEMPLATE_ROOT / 'docker'
        if not source_docker.exists():
            print('  ⚠️  Docker templates not found')
            return
        target_docker = self.projectRoot / 'docker'
        self.ensureDirectoryExists(target_docker)
        docker_files = [
            ('docker-dev.template.yml', 'docker/docker-compose.dev.yml'),
            ('Dockerfile.dev.template', 'docker/Dockerfile.dev'),
            ('.env.docker.example', 'docker/.env.docker.example'),
            ('.dockerignore', '.dockerignore'),
            ('docker-scripts.sh', 'docker-scripts.sh'),
        ]
        copied = 0
        for src_name, dest_name in docker_files:
            src = source_docker / src_name
            dest = self.projectRoot / dest_name
            if src.exists() and not dest.exists():
                self.ensureDirectoryExists(dest.parent)
                shutil.copy2(src, dest)
                if dest.suffix == '.sh' or dest.name.endswith('.sh'):
                    try:
                        os.chmod(dest, 0o755)
                    except OSError:
                        pass
                copied += 1
                print(f"  ✅ Created {dest_name}")
        if copied:
            print('  ✅ Docker development environment ready!')
            print('     Run: ./docker-scripts.sh dev-up')
        else:
            print('  ℹ️  Docker files already exist')

    def getTemplateVersion(self) -> str:
        version_file = TEMPLATE_ROOT / 'VERSION'
        if version_file.exists():
            try:
                data = json.loads(version_file.read_text(encoding='utf-8'))
                return data.get('version', 'unknown')
            except json.JSONDecodeError:
                for line in version_file.read_text(encoding='utf-8').splitlines():
                    if line.lower().startswith('version'):
                        return line.split(':', 1)[1].strip()
        return 'unknown'

    def run(self, argv: Optional[Iterable[str]] = None) -> None:
        self.args = list(argv or [])
        print("🚀 Starting comprehensive project sync...\n")
        self.detectTechStack()
        self.syncVSCodeSettings()
        self.updateAgentContexts()
        self.syncAgentFiles()
        self.syncGitHubWorkflows()
        self.syncGitHubIssueTemplates()
        self.syncVersioningSystem()
        self.syncMcpConfigurations()
        self.syncClaudeDirectory()
        self.syncDockerTemplates()
        self.syncProjectEssentials()
        self.syncTestingStructure()
        self.syncDevOpsSystem()
        self.runDevOpsSetup()
        self.createTemplateVersionTracking()
        self.registerForTemplateUpdates()
        print("\n✅ Project sync completed successfully!")

    updateVscodeSettings = updateVSCodeSettings

def main(argv: Optional[Iterable[str]] = None) -> int:
    sync = ProjectSync()
    sync.run(argv or sys.argv[1:])
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
