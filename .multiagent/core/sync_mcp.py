import json
from pathlib import Path

def load_json_file(file_path):
    """Load a JSON file and return the data, or None if it fails"""
    try:
        if not file_path.exists():
            return None
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"[ERROR] Error loading {file_path}: {e}")
        return None

def deep_merge(base_dict, override_dict):
    """Deep merge two dictionaries"""
    if not override_dict:
        return base_dict
    
    result = base_dict.copy()
    for key, value in override_dict.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result

def get_claude_mcp_config_path():
    home_dir = Path.home()
    # This is a simplified path resolution
    return home_dir / '.config' / 'claude' / 'claude_desktop_config.json'

def load_global_agent_configs():
    """Load MCP configurations from global agent directories"""
    home_dir = Path.home()
    agent_configs = {}
    
    for agent in ['claude', 'gemini', 'qwen', 'codex']:
        config_path = home_dir / f'.{agent}' / 'mcp-config.json'
        if config_path.exists():
            agent_config = load_json_file(config_path)
            if agent_config:
                agent_configs[agent] = agent_config
                print(f"[OK] Loaded {agent} MCP config from {config_path}")
        else:
            print(f"[WARN] No MCP config found for {agent} at {config_path}")
    
    return agent_configs

def sync_mcp_configurations():
    print("[SYNC] Syncing shared MCP configurations...")
    
    project_root = Path(__file__).resolve().parent.parent.parent
    templates_dir = project_root / '.multiagent' / 'templates'
    overrides_dir = project_root / '.multiagent' / 'local-overrides'

    # Load shared template
    shared_mcp_template = load_json_file(templates_dir / 'shared-mcp.template.json')
    if not shared_mcp_template:
        print("[ERROR] No shared MCP template found")
        return

    # Load global agent configurations
    agent_configs = load_global_agent_configs()
    
    # Load local overrides
    mcp_overrides = load_json_file(overrides_dir / 'mcp-local.json')
    if mcp_overrides:
        print("[CONFIG] Loaded local MCP overrides")

    # Merge configurations in priority order: agent configs -> shared template -> local overrides
    merged_mcp_config = shared_mcp_template.copy()
    
    # Merge agent-specific servers
    for agent, config in agent_configs.items():
        if 'servers' in config:
            if 'servers' not in merged_mcp_config:
                merged_mcp_config['servers'] = {}
            merged_mcp_config['servers'].update(config['servers'])
        
        # Merge inputs from all agents
        if 'inputs' in config:
            if 'inputs' not in merged_mcp_config:
                merged_mcp_config['inputs'] = []
            
            # Add unique inputs only
            existing_ids = {inp.get('id') for inp in merged_mcp_config['inputs']}
            for inp in config['inputs']:
                if inp.get('id') not in existing_ids:
                    merged_mcp_config['inputs'].append(inp)

    # Apply local overrides last
    if mcp_overrides:
        merged_mcp_config = deep_merge(merged_mcp_config, mcp_overrides)

    # Update project's VS Code MCP config
    vscode_mcp_path = project_root / '.vscode' / 'mcp.json'
    vscode_mcp_path.write_text(json.dumps(merged_mcp_config, indent=2))
    print(f"[OK] Updated project MCP config: {vscode_mcp_path}")

    # Update Claude desktop config
    claude_config_path = get_claude_mcp_config_path()
    claude_config_path.parent.mkdir(parents=True, exist_ok=True)

    existing_claude_config = load_json_file(claude_config_path) or {}
    
    claude_config = {
        **existing_claude_config,
        "mcpServers": {
            **existing_claude_config.get("mcpServers", {}),
            **merged_mcp_config.get("servers", {})
        }
    }
    
    claude_config_path.write_text(json.dumps(claude_config, indent=2))
    print(f"[OK] Updated Claude Code MCP config: {claude_config_path}")
    
    print('\n[SUCCESS] Shared MCP configuration sync complete!')

if __name__ == "__main__":
    try:
        sync_mcp_configurations()
    except Exception as e:
        print(f"[ERROR] Error syncing MCP configs: {e}")
        exit(1)
