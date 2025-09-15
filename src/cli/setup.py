"""
Post-installation setup for SignalHire Agent
"""

import os
import sys
from pathlib import Path


def post_install():
    """Run post-installation setup tasks."""
    try:
        # Create .env file if it doesn't exist
        env_file = Path(".env")
        if not env_file.exists():
            env_content = """# SignalHire Agent Configuration
# Get your API key from SignalHire support
SIGNALHIRE_API_KEY=your_api_key_here

# Optional: Alternative authentication (choose one method)
# SIGNALHIRE_EMAIL=your@email.com
# SIGNALHIRE_PASSWORD=your_password

# Optional: API Configuration
# SIGNALHIRE_API_BASE_URL=https://api.signalhire.com
# SIGNALHIRE_API_PREFIX=/api/v1
"""
            env_file.write_text(env_content)
            print("✅ Created .env configuration file")
        
        print("🎉 SignalHire Agent setup complete!")
        print("\nNext steps:")
        print("1. Edit .env file with your SignalHire API key")
        print("2. Run: signalhire-agent doctor")
        print("3. Start searching: signalhire-agent search --help")
        
    except Exception as e:
        print(f"⚠️  Setup warning: {e}")


if __name__ == "__main__":
    post_install()