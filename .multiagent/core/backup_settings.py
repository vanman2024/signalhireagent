import os
import shutil
from datetime import datetime
from pathlib import Path

def get_vscode_settings_path():
    """Gets the platform-specific VS Code settings path."""
    platform = os.name
    home_dir = Path.home()
    if platform == 'nt':
        return home_dir / 'AppData' / 'Roaming' / 'Code' / 'User' / 'settings.json'
    elif platform == 'darwin':
        return home_dir / 'Library' / 'Application Support' / 'Code' / 'User' / 'settings.json'
    else: # linux
        return home_dir / '.config' / 'Code' / 'User' / 'settings.json'

def backup_settings():
    """Creates backups of current VS Code and other settings."""
    print("💾 Creating settings backup...")
    backup_dir = Path(__file__).parent.parent / 'backups'
    backup_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().isoformat().replace(':', '-').replace('.', '-')

    # Backup VS Code settings
    vscode_settings_path = get_vscode_settings_path()
    if vscode_settings_path.exists():
        backup_path = backup_dir / f"vscode-settings-{timestamp}.json"
        shutil.copy2(vscode_settings_path, backup_path)
        print(f"✅ Backed up VS Code settings: {backup_path}")
    else:
        print("⚠️  VS Code settings file not found, skipping backup")

    # Backup project .vscode/settings.json if it exists
    project_root = Path(__file__).resolve().parent.parent.parent
    project_settings_path = project_root / '.vscode' / 'settings.json'
    if project_settings_path.exists():
        backup_path = backup_dir / f"project-vscode-settings-{timestamp}.json"
        shutil.copy2(project_settings_path, backup_path)
        print(f"✅ Backed up project VS Code settings: {backup_path}")

    print("\n📋 Available backups:")
    backup_files = sorted(
        [f for f in backup_dir.glob('*.json')],
        key=os.path.getmtime,
        reverse=True
    )
    for i, f in enumerate(backup_files[:10]):
        mtime = datetime.fromtimestamp(f.stat().st_mtime)
        print(f"  {i + 1}. {f.name} ({mtime.strftime('%Y-%m-%d %H:%M:%S')})")

if __name__ == "__main__":
    try:
        backup_settings()
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        exit(1)
