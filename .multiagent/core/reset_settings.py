import os
import shutil
from datetime import datetime
from pathlib import Path
from backup_settings import backup_settings, get_vscode_settings_path

def reset_settings():
    """Restores settings from a backup."""
    print("🔄 Reset Settings from Backup")
    backup_dir = Path(__file__).parent.parent / 'backups'

    if not backup_dir.exists():
        print("❌ No backup directory found. Run backup_settings first.")
        return

    backup_files = sorted(
        [f for f in backup_dir.glob('*.json')],
        key=os.path.getmtime,
        reverse=True
    )

    if not backup_files:
        print("❌ No backup files found.")
        return

    print("\n📋 Available backups:")
    for i, f in enumerate(backup_files):
        mtime = datetime.fromtimestamp(f.stat().st_mtime)
        print(f"  {i + 1}. {f.name} ({mtime.strftime('%Y-%m-%d %H:%M:%S')})")

    try:
        selection = input(f"\nSelect backup to restore (1-{len(backup_files)}, or 'q' to quit): ")
        if selection.lower() == 'q':
            print("Operation cancelled.")
            return

        index = int(selection) - 1
        if not (0 <= index < len(backup_files)):
            print("❌ Invalid selection.")
            return

        selected_backup = backup_files[index]
        confirm = input(f"\n⚠️  This will overwrite your current settings with: {selected_backup.name}\nContinue? (y/N): ")
        if confirm.lower() not in ['y', 'yes']:
            print("Operation cancelled.")
            return

        print("\n💾 Creating backup of current settings before restore...")
        backup_settings()

        vscode_settings_path = get_vscode_settings_path()
        vscode_settings_path.parent.mkdir(exist_ok=True)
        shutil.copy2(selected_backup, vscode_settings_path)
        print(f"\n✅ Restored settings from: {selected_backup.name}")
        print(f"📍 Applied to: {vscode_settings_path}")

        if 'project-vscode' in selected_backup.name:
            project_root = Path(__file__).resolve().parent.parent.parent
            project_settings_path = project_root / '.vscode' / 'settings.json'
            project_settings_path.parent.mkdir(exist_ok=True)
            shutil.copy2(selected_backup, project_settings_path)
            print(f"📍 Also applied to project: {project_settings_path}")

        print("\n🎉 Settings restored successfully!")
        print("💡 Restart VS Code to ensure all settings take effect.")

    except (ValueError, IndexError):
        print("❌ Invalid selection.")
    except Exception as e:
        print(f"❌ Error restoring settings: {e}")

if __name__ == "__main__":
    reset_settings()
