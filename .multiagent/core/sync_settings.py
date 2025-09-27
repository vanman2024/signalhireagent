import json
import os
from pathlib import Path
import shutil
from datetime import datetime
from backup_settings import get_vscode_settings_path

def deep_merge(target, source):
    """Deep merges two dictionaries."""
    result = target.copy()
    for key, value in source.items():
        if isinstance(value, dict) and key in result and isinstance(result[key], dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result

def load_json_file(file_path):
    """Loads a JSON file, ignoring comments."""
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return {}
    try:
        # A simple way to strip comments for JSON parsing
        import re
        content = file_path.read_text()
        content = re.sub(r"//.*", "", content)
        content = re.sub(r"/\*[\s\S]*?\*/", "", content, flags=re.MULTILINE)
        return json.loads(content)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error parsing {file_path}: {e}")
        return {}

def sync_settings():
    """Merges current VS Code settings with local overrides and applies to VS Code."""
    print("🔄 Syncing settings...")
    project_root = Path(__file__).resolve().parent.parent.parent
    templates_dir = project_root / '.multiagent' / 'templates'
    overrides_dir = project_root / '.multiagent' / 'local-overrides'

    # Use current VS Code settings as base instead of template
    vscode_settings_path = get_vscode_settings_path()
    if vscode_settings_path.exists():
        template_settings = load_json_file(vscode_settings_path)
        print(f"📝 Loaded current VS Code settings: {vscode_settings_path}")
    else:
        # Fallback to template if no current settings
        template_path = templates_dir / 'vscode-settings.template.json'
        template_settings = load_json_file(template_path)
        print(f"📝 Loaded template: {template_path}")

    override_path = overrides_dir / 'vscode-local.json'
    local_overrides = load_json_file(override_path)
    if local_overrides:
        print(f"🔧 Loaded local overrides: {override_path}")

    merged_settings = deep_merge(template_settings, local_overrides)

    vscode_settings_path = get_vscode_settings_path()
    backup_dir = project_root / '.multiagent' / 'backups'
    backup_dir.mkdir(exist_ok=True)

    if vscode_settings_path.exists():
        timestamp = datetime.now().isoformat().replace(':', '-').replace('.', '-')
        backup_path = backup_dir / f"settings-backup-{timestamp}.json"
        shutil.copy2(vscode_settings_path, backup_path)
        print(f"💾 Backed up current settings to: {backup_path}")

    vscode_settings_path.parent.mkdir(exist_ok=True)
    vscode_settings_path.write_text(json.dumps(merged_settings, indent=2))
    print(f"✅ Applied settings to: {vscode_settings_path}")

    project_settings_path = project_root / '.vscode' / 'settings.json'
    if project_settings_path.parent.exists():
        project_settings_path.write_text(json.dumps(merged_settings, indent=2))
        print(f"✅ Updated project settings: {project_settings_path}")

    print("🎉 Settings sync complete!")
    
    # Also sync MCP configurations
    try:
        from .sync_mcp import sync_mcp_configurations
        sync_mcp_configurations()
        
        # Sync agent-specific MCP configurations
        from .sync_agent_mcp import sync_all_agent_mcp
        sync_all_agent_mcp()
    except ImportError:
        print("⚠️  MCP sync not available")
    except Exception as e:
        print(f"❌ Error syncing MCP configs: {e}")

if __name__ == "__main__":
    try:
        sync_settings()
    except Exception as e:
        print(f"❌ Error syncing settings: {e}")
        exit(1)
