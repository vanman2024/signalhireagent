#!/usr/bin/env python3
"""
Sync MCP server configurations to all agent CLIs
"""
import json
import toml
from pathlib import Path

def get_github_token():
    """Get GitHub token from gh CLI"""
    import subprocess
    try:
        result = subprocess.run(['gh', 'auth', 'token'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return "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"  # fallback

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

def save_json_file(file_path, data):
    """Save data to a JSON file"""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"[ERROR] Error saving {file_path}: {e}")
        return False

def save_toml_file(file_path, data):
    """Save data to a TOML file"""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            toml.dump(data, f)
        return True
    except Exception as e:
        print(f"[ERROR] Error saving {file_path}: {e}")
        return False

def sync_gemini_mcp():
    """Sync MCP configuration for Gemini CLI"""
    print("[SYNC] Updating Gemini MCP configuration...")
    
    home_dir = Path.home()
    settings_path = home_dir / '.gemini' / 'settings.json'
    
    if not settings_path.exists():
        print(f"[WARN] Gemini settings file not found: {settings_path}")
        return False
    
    settings = load_json_file(settings_path)
    if not settings:
        return False
    
    github_token = get_github_token()
    
    # Add MCP configuration
    settings["mcp"] = {
        "allowed": ["filesystem", "github", "memory", "playwright", "postman"]
    }
    
    settings["mcpServers"] = {
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/vanman2025"]
        },
        "github": {
            "httpUrl": "https://api.githubcopilot.com/mcp/",
            "trust": True,
            "headers": {
                "Authorization": f"Bearer {github_token}"
            }
        },
        "memory": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-memory"]
        },
        "playwright": {
            "command": "npx",
            "args": ["@playwright/mcp@latest"]
        },
        "postman": {
            "command": "npx",
            "args": ["-y", "@postman/postman-mcp-server"],
            "env": {
                "POSTMAN_API_KEY": "PMAK-68a819ab04b03100014ed381-6ad8f68ff14db0950c98040e199f92b18c"
            }
        }
    }
    
    if save_json_file(settings_path, settings):
        print(f"[OK] Updated Gemini MCP config: {settings_path}")
        return True
    return False

def sync_qwen_mcp():
    """Sync MCP configuration for Qwen CLI"""
    print("[SYNC] Updating Qwen MCP configuration...")
    
    home_dir = Path.home()
    settings_path = home_dir / '.qwen' / 'settings.json'
    
    if not settings_path.exists():
        print(f"[WARN] Qwen settings file not found: {settings_path}")
        return False
    
    settings = load_json_file(settings_path)
    if not settings:
        return False
    
    github_token = get_github_token()
    
    # Add MCP configuration
    settings["mcp"] = {
        "allowed": ["filesystem", "github", "memory", "playwright", "postman"]
    }
    
    settings["mcpServers"] = {
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/vanman2025"]
        },
        "github": {
            "httpUrl": "https://api.githubcopilot.com/mcp/",
            "trust": True,
            "headers": {
                "Authorization": f"Bearer {github_token}"
            }
        },
        "memory": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-memory"]
        },
        "playwright": {
            "command": "npx",
            "args": ["@playwright/mcp@latest"]
        },
        "postman": {
            "command": "npx",
            "args": ["-y", "@postman/postman-mcp-server"],
            "env": {
                "POSTMAN_API_KEY": "PMAK-68a819ab04b03100014ed381-6ad8f68ff14db0950c98040e199f92b18c"
            }
        }
    }
    
    if save_json_file(settings_path, settings):
        print(f"[OK] Updated Qwen MCP config: {settings_path}")
        return True
    return False

def sync_codex_mcp():
    """Sync MCP configuration for Codex CLI"""
    print("[SYNC] Updating Codex MCP configuration...")
    
    home_dir = Path.home()
    config_path = home_dir / '.codex' / 'config.toml'
    
    if not config_path.exists():
        print(f"[WARN] Codex config file not found: {config_path}")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = toml.load(f)
    except Exception as e:
        print(f"[ERROR] Error loading Codex config: {e}")
        return False
    
    github_token = get_github_token()
    
    # Add MCP server configurations
    config["mcp_servers"] = {
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/vanman2025"]
        },
        "github": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {"GITHUB_TOKEN": github_token}
        },
        "memory": {
            "command": "npx", 
            "args": ["-y", "@modelcontextprotocol/server-memory"]
        },
        "playwright": {
            "command": "npx",
            "args": ["@playwright/mcp@latest"]
        },
        "postman": {
            "command": "npx",
            "args": ["-y", "@postman/postman-mcp-server"],
            "env": {"POSTMAN_API_KEY": "PMAK-68a819ab04b03100014ed381-6ad8f68ff14db0950c98040e199f92b18c"}
        }
    }
    
    if save_toml_file(config_path, config):
        print(f"[OK] Updated Codex MCP config: {config_path}")
        return True
    return False

def sync_claude_mcp():
    """Claude CLI is configured via claude mcp add commands - skip file-based config"""
    print("[SKIP] Claude Code CLI uses 'claude mcp add' commands - already configured")
    return True

def sync_all_agent_mcp():
    """Sync MCP configurations for all agents"""
    print("[SYNC] Syncing MCP configurations for all agents...")
    
    results = []
    results.append(sync_gemini_mcp())
    results.append(sync_qwen_mcp())
    results.append(sync_codex_mcp())
    results.append(sync_claude_mcp())
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f"\n[RESULT] {success_count}/{total_count} agent MCP configurations updated successfully")
    
    if success_count == total_count:
        print("[SUCCESS] All agent MCP configurations synced!")
    else:
        print("[WARN] Some agent configurations failed to update")
    
    return success_count == total_count

if __name__ == "__main__":
    try:
        sync_all_agent_mcp()
    except Exception as e:
        print(f"[ERROR] Error syncing agent MCP configs: {e}")
        exit(1)