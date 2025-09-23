import json
from pathlib import Path
from .sync_settings import sync_settings

def setup_new_project():
    print("🚀 Setting up development settings for new project...")
    
    multiagent_dir = Path(__file__).parent.parent
    overrides_dir = multiagent_dir / 'local-overrides'
    backups_dir = multiagent_dir / 'backups'

    overrides_dir.mkdir(exist_ok=True)
    backups_dir.mkdir(exist_ok=True)

    # Example override files can be created here if needed
    
    print('\n✅ Project setup complete! Next steps:')
    print('1. Edit files in local-overrides/ to customize for this project')
    print('2. Run sync_settings to apply settings to .vscode/')
    
    print('\n🔄 Running initial sync...')
    try:
        sync_settings()
    except Exception as e:
        print(f"❌ Error during initial sync: {e}")

if __name__ == "__main__":
    try:
        setup_new_project()
    except Exception as e:
        print(f"❌ Error setting up new project: {e}")
        exit(1)
