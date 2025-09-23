import os
import shutil
import subprocess
from pathlib import Path

class TemplateUpdater:
    def __init__(self):
        self.template_repo = 'https://github.com/vanman2024/multi-agent-claude-code.git'
        self.temp_dir = Path('/tmp/template-update')
        self.project_root = Path.cwd()
        self.template_version_file = '.template-version'
        self.safe_update_paths = [
            'devops/',
            'agentswarm/',
            'agents/',
            '.github/workflows/version-management.yml',
            'scripts/ops',
        ]

    def get_latest_template_version(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        print('🔍 Checking latest template version...')
        subprocess.run(['git', 'clone', '--depth', '1', self.template_repo, str(self.temp_dir)], check=True, capture_output=True)
        
        version_file = self.temp_dir / 'VERSION'
        if version_file.exists():
            # Simplified version parsing
            return "latest"
        return None

    def update_project(self, force=False, preview=False):
        print('\n🚀 Starting template update...')
        self.get_latest_template_version()
        changes = []

        for safe_path_str in self.safe_update_paths:
            template_path = self.temp_dir / safe_path_str
            project_path = self.project_root / safe_path_str
            if template_path.exists():
                if template_path.is_dir():
                    self.update_directory(template_path, project_path, changes, preview)
                else:
                    self.update_file(template_path, project_path, changes, preview)
        
        if preview:
            print('\n📋 Preview of changes:')
            for change in changes: print(f"   {change}")
            return

        if not changes:
            print('\n✅ No changes needed.')
            return
            
        print('\n✅ Template update completed!')
        print(f'📝 Applied {len(changes)} changes:')
        for change in changes: print(f"   • {change}")

    def update_directory(self, template_dir, project_dir, changes, preview):
        for item in template_dir.iterdir():
            project_item = project_dir / item.name
            if item.is_dir():
                self.update_directory(item, project_item, changes, preview)
            else:
                self.update_file(item, project_item, changes, preview)

    def update_file(self, template_file, project_file, changes, preview):
        template_content = template_file.read_bytes()
        if project_file.exists() and project_file.read_bytes() == template_content:
            return

        relative_path = project_file.relative_to(self.project_root)
        if not preview:
            project_file.parent.mkdir(parents=True, exist_ok=True)
            project_file.write_bytes(template_content)
        
        changes.append(f"Updated {relative_path}" if project_file.exists() else f"Created {relative_path}")

if __name__ == '__main__':
    import sys
    args = sys.argv[1:]
    options = {
        "force": '--force' in args,
        "preview": '--preview' in args,
        "check": '--check' in args
    }
    updater = TemplateUpdater()
    if options['check']:
        # Simplified check
        updater.get_latest_template_version()
        print("Checked for updates.")
    else:
        updater.update_project(**options)
