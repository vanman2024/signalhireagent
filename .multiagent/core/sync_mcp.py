import json
from pathlib import Path
from .sync_settings import load_json_file, deep_merge

def get_claude_mcp_config_path():
    home_dir = Path.home()
    # This is a simplified path resolution
    return home_dir / '.config' / 'claude' / 'claude_desktop_config.json'

def sync_mcp_configurations():
    print("🔗 Syncing shared MCP configurations...")
    
    project_root = Path(__file__).resolve().parent.parent.parent
    templates_dir = project_root / '.multiagent' / 'templates'
    overrides_dir = project_root / '.multiagent' / 'local-overrides'

    shared_mcp_template = load_json_file(templates_dir / 'shared-mcp.template.json')
    if not shared_mcp_template:
        print("❌ No shared MCP template found")
        return

    mcp_overrides = load_json_file(overrides_dir / 'mcp-local.json')
    if mcp_overrides:
        print("🔧 Loaded local MCP overrides")

    merged_mcp_config = deep_merge(shared_mcp_template, mcp_overrides)

    claude_config_path = get_claude_mcp_config_path()
    claude_config_path.parent.mkdir(exist_ok=True)

    existing_claude_config = load_json_file(claude_config_path)
    
    claude_config = {
        **existing_claude_config,
        "mcpServers": {
            **existing_claude_config.get("mcpServers", {}),
            **merged_mcp_config.get("mcpServers", {})
        }
    }
    
    claude_config_path.write_text(json.dumps(claude_config, indent=2))
    print(f"✅ Updated Claude Code MCP config: {claude_config_path}")
    
    print('\n🎉 Shared MCP configuration sync complete!')

if __name__ == "__main__":
    try:
        sync_mcp_configurations()
    except Exception as e:
        print(f"❌ Error syncing MCP configs: {e}")
        exit(1)
