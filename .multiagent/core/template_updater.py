import hashlib
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

class TemplateUpdateSystem:
    """
    Detects changes in a template repository and provides update mechanisms
    for deployed projects to stay synchronized.
    """

    def __init__(self, project_root=None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.template_repo = 'https://github.com/vanman2024/multi-agent-claude-code.git'
        self.template_version_file = self.project_root / '.template-version'
        self.update_cache_dir = self.project_root / '.template-cache'
        self.critical_paths = [
            'devops/',
            'agentswarm/',
            '.multiagent/templates/',
            '.multiagent/tools/ops',
            '.github/workflows/',
            '.claude/hooks/',
            '.multiagent/core/sync-project.js' # This should be updated to sync_project.py post-conversion
        ]

    def check_for_updates(self, details=False):
        """Checks if updates are available from the template repository."""
        print("🔍 Checking for template updates...")
        try:
            current_version = self._get_current_template_version()
            latest_version = self._get_latest_template_version()

            if current_version == latest_version:
                print("✅ Project is up to date with template.")
                return {"has_updates": False, "current_version": current_version, "latest_version": latest_version}

            changes = self._get_changes_since(current_version)
            critical_changes = self._filter_critical_changes(changes)

            print("📦 Template updates available:")
            print(f"   Current: {current_version}")
            print(f"   Latest: {latest_version}")
            print(f"   Changes in critical paths: {len(critical_changes)}")

            if details:
                self._show_update_details(critical_changes)

            return {
                "has_updates": True,
                "current_version": current_version,
                "latest_version": latest_version,
                "changes": critical_changes,
                "all_changes": changes,
            }
        except Exception as e:
            print(f"❌ Failed to check for updates: {e}")
            return {"has_updates": False, "error": str(e)}

    def preview_updates(self):
        """Previews what would be updated without applying changes."""
        print("👀 Previewing template updates...")
        update_info = self.check_for_updates(details=True)
        if not update_info.get("has_updates"):
            return update_info

        temp_dir = self._clone_template_to_temp()
        try:
            preview = {"files_to_update": [], "files_to_add": [], "conflicting_files": [], "backup_required": []}
            for change in update_info.get("changes", []):
                analysis = self._analyze_file_change(change, temp_dir)
                if analysis["has_conflict"]:
                    preview["conflicting_files"].append(analysis)
                elif analysis["is_new"]:
                    preview["files_to_add"].append(analysis)
                else:
                    preview["files_to_update"].append(analysis)
                if analysis["needs_backup"]:
                    preview["backup_required"].append(analysis)
            
            self._show_preview_summary(preview)
            return {**update_info, "preview": preview}
        finally:
            shutil.rmtree(temp_dir)

    def apply_updates(self, auto_resolve=False, run_sync=False):
        """Applies template updates to the current project."""
        print("🔄 Applying template updates...")
        preview_info = self.preview_updates()
        if not preview_info.get("has_updates"):
            return preview_info

        backup_dir = self._create_backup()
        print(f"💾 Created backup at: {backup_dir}")

        try:
            results = {"updated": [], "added": [], "conflicts": [], "errors": []}
            
            # Apply non-conflicting updates and add new files
            for file_info in preview_info["preview"]["files_to_update"] + preview_info["preview"]["files_to_add"]:
                try:
                    self._update_or_add_file(file_info)
                    if file_info['is_new']:
                        results["added"].append(file_info["path"])
                        print(f"  ✅ Added {file_info['path']}")
                    else:
                        results["updated"].append(file_info["path"])
                        print(f"  ✅ Updated {file_info['path']}")
                except Exception as e:
                    results["errors"].append({"path": file_info["path"], "error": str(e)})
                    print(f"  ❌ Failed to process {file_info['path']}: {e}")

            # Handle conflicts
            for file_info in preview_info["preview"]["conflicting_files"]:
                if auto_resolve:
                    try:
                        self._auto_resolve_conflict(file_info)
                        results["updated"].append(file_info["path"])
                        print(f"  ✅ Auto-resolved conflict in {file_info['path']}")
                    except Exception as e:
                        results["errors"].append({"path": file_info["path"], "error": str(e)})
                        print(f"  ❌ Failed to auto-resolve {file_info['path']}: {e}")
                else:
                    results["conflicts"].append(file_info["path"])
                    print(f"  ⚠️  Skipped conflicting file {file_info['path']} (use --auto-resolve to force)")

            self._update_template_version(preview_info["latest_version"])
            self._print_summary(results)

            if not results["errors"] and not results["conflicts"] and run_sync:
                print("\n🔄 Running project sync to apply updates...")
                subprocess.run(['node', '.multiagent/core/sync-project.js'], cwd=self.project_root, check=True)

            return {**preview_info, "results": results, "backup_dir": backup_dir}
        except Exception as e:
            print("❌ Update failed, restoring from backup...")
            self._restore_from_backup(backup_dir)
            raise e

    def _get_current_template_version(self):
        if not self.template_version_file.exists():
            return 'unknown'
        content = self.template_version_file.read_text()
        match = [line for line in content.splitlines() if line.startswith('TEMPLATE_VERSION=')]
        return match[0].split('=')[1].strip() if match else 'unknown'

    def _get_latest_template_version(self):
        result = subprocess.run(['git', 'ls-remote', self.template_repo, 'HEAD'], capture_output=True, text=True, check=True)
        return result.stdout.split('\t')[0][:8]

    def _get_changes_since(self, version):
        temp_dir = self._clone_template_to_temp()
        try:
            changes = []
            for p in self.critical_paths:
                source_path = temp_dir / p
                if source_path.exists():
                    if source_path.is_dir():
                        for file_path in source_path.rglob('*'):
                            if file_path.is_file():
                                relative_path = file_path.relative_to(temp_dir).as_posix()
                                changes.append({"path": relative_path, "type": "modified", "priority": self._get_change_priority(relative_path)})
                    else:
                        changes.append({"path": p, "type": "modified", "priority": self._get_change_priority(p)})
            return changes
        finally:
            shutil.rmtree(temp_dir)

    def _filter_critical_changes(self, changes):
        return [change for change in changes if any(change["path"].startswith(p) for p in self.critical_paths)]

    def _get_change_priority(self, file_path):
        if 'devops/' in file_path or 'agentswarm/' in file_path:
            return 'high'
        elif '.github/workflows/' in file_path or 'scripts/' in file_path:
            return 'medium'
        return 'low'

    def _clone_template_to_temp(self):
        temp_dir = self.update_cache_dir / f"template-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(['git', 'clone', '--depth', '1', self.template_repo, str(temp_dir)], check=True, capture_output=True)
        return temp_dir

    def _analyze_file_change(self, change, temp_dir):
        temp_file_path = temp_dir / change["path"]
        project_file_path = self.project_root / change["path"]
        analysis = {
            "path": change["path"],
            "priority": change["priority"],
            "is_new": not project_file_path.exists(),
            "has_conflict": False,
            "needs_backup": False,
            "temp_path": temp_file_path,
            "project_path": project_file_path,
        }
        if not analysis["is_new"] and temp_file_path.exists():
            temp_hash = self._get_file_hash(temp_file_path)
            project_hash = self._get_file_hash(project_file_path)
            if temp_hash != project_hash:
                analysis["has_conflict"] = True  # Simplified logic
                analysis["needs_backup"] = True
        return analysis

    def _get_file_hash(self, file_path):
        return hashlib.md5(file_path.read_bytes()).hexdigest()

    def _show_update_details(self, changes):
        # Implementation for showing details
        pass

    def _show_preview_summary(self, preview):
        # Implementation for showing summary
        pass

    def _create_backup(self):
        timestamp = datetime.now().isoformat().replace(':', '-').replace('.', '-')
        backup_dir = self.update_cache_dir / f"backup-{timestamp}"
        backup_dir.mkdir(parents=True)
        for p_str in self.critical_paths:
            source_path = self.project_root / p_str
            backup_path = backup_dir / p_str
            if source_path.exists():
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                if source_path.is_dir():
                    shutil.copytree(source_path, backup_path)
                else:
                    shutil.copy2(source_path, backup_path)
        return backup_dir

    def _update_or_add_file(self, file_info):
        if not file_info["temp_path"].exists():
            raise FileNotFoundError(f"Template file not found: {file_info['temp_path']}")
        file_info["project_path"].parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_info["temp_path"], file_info["project_path"])

    def _auto_resolve_conflict(self, file_info):
        print(f"   🔧 Auto-resolving conflict in {file_info['path']}")
        self._update_or_add_file(file_info)

    def _update_template_version(self, new_version):
        content = f"""TEMPLATE_VERSION={new_version}
TEMPLATE_REPO={self.template_repo}
SYNC_DATE={datetime.now().date().isoformat()}
LAST_UPDATE={datetime.now().isoformat()}
"""
        self.template_version_file.write_text(content)

    def _restore_from_backup(self, backup_dir):
        print(f"🔄 Restoring from backup at {backup_dir}...")
        for item in backup_dir.iterdir():
            target_path = self.project_root / item.name
            if item.is_dir():
                shutil.rmtree(target_path, ignore_errors=True)
                shutil.copytree(item, target_path)
            else:
                shutil.copy2(item, target_path)
        print("✅ Restored from backup.")

    def _print_summary(self, results):
        print("\n📊 Update Summary:")
        print(f"   Files updated: {len(results['updated'])}")
        print(f"   Files added: {len(results['added'])}")
        print(f"   Conflicts: {len(results['conflicts'])}")
        print(f"   Errors: {len(results['errors'])}")
        if results['conflicts']:
            print("\n⚠️  Manual Resolution Needed:")
            for path in results['conflicts']:
                print(f"   - {path}")
