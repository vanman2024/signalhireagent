#!/bin/bash

echo "🚀 Setting up SignalHire Agent..."

# Show help if requested
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: ./setup.sh [version]"
    echo ""
    echo "Version options:"
    echo "  --stable        Use latest stable release (recommended)"
    echo "  --latest-tag    Same as --stable"
    echo "  v0.1.0          Use specific version tag"
    echo "  main            Use latest development code (default)"
    echo ""
    echo "Examples:"
    echo "  ./setup.sh --stable     # Use latest stable version"
    echo "  ./setup.sh v0.1.0       # Use specific version"
    echo "  ./setup.sh              # Use current branch"
    exit 0
fi

# Check if we should use a stable version
if [ "$1" = "--stable" ] || [ "$1" = "--latest-tag" ]; then
    echo "📌 Switching to latest stable version..."
    LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null)
    if [ -n "$LATEST_TAG" ]; then
        git checkout "$LATEST_TAG"
        echo "✅ Using stable version: $LATEST_TAG"
    else
        echo "⚠️  No tags found, using current branch"
    fi
elif [ -n "$1" ]; then
    echo "📌 Switching to specified version: $1"
    git checkout "$1"
fi

# Make the launcher script globally available
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAUNCHER_PATH="$SCRIPT_DIR/signalhire-agent"

# Create ~/.local/bin if it doesn't exist
mkdir -p "$HOME/.local/bin"

# Try to add to user's local bin (most common approach)
if [ -d "$HOME/.local/bin" ]; then
    ln -sf "$LAUNCHER_PATH" "$HOME/.local/bin/signalhire-agent"
    echo "✅ Added signalhire-agent to ~/.local/bin"
    
    # Add ~/.local/bin to PATH if not already there
    if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
        echo "📝 Adding ~/.local/bin to PATH..."
        
        # Add to appropriate shell profile
        if [ -f "$HOME/.bashrc" ]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
            echo "✅ Updated ~/.bashrc"
        fi
        if [ -f "$HOME/.zshrc" ]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
            echo "✅ Updated ~/.zshrc"
        fi
        
        # Update current session
        export PATH="$HOME/.local/bin:$PATH"
        echo "✅ Updated current session PATH"
    fi
    
    GLOBAL_INSTALL=true
elif [ -w "/usr/local/bin" ]; then
    ln -sf "$LAUNCHER_PATH" "/usr/local/bin/signalhire-agent" 
    echo "✅ Added signalhire-agent to /usr/local/bin"
    GLOBAL_INSTALL=true
else
    echo "⚠️  Cannot add to PATH, use ./signalhire-agent instead"
    GLOBAL_INSTALL=false
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env configuration file..."
    cat > .env << 'EOF'
# SignalHire Agent Configuration
# 
# REQUIRED: Get your API key from SignalHire
# 1. Contact SignalHire support: support@signalhire.com
# 2. Request API access for lead generation
# 3. Replace the line below with your actual API key
SIGNALHIRE_API_KEY=your_api_key_here

# Optional: Alternative authentication (choose one method)
# SIGNALHIRE_EMAIL=your@email.com
# SIGNALHIRE_PASSWORD=your_password

# Optional: API Configuration (use defaults unless advised otherwise)
# SIGNALHIRE_API_BASE_URL=https://api.signalhire.com
# SIGNALHIRE_API_PREFIX=/api/v1
EOF
    echo "✅ Created .env file"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 SignalHire Agent setup complete!"
echo ""
echo "Next steps:"
echo "1. Get your SignalHire API key:"
echo "   • Contact SignalHire support: support@signalhire.com"
echo "   • Request API access for lead generation"
echo ""
echo "2. Edit .env file with your actual API key:"
echo "   nano .env"
echo "   # Replace: SIGNALHIRE_API_KEY=your_api_key_here"
echo "   # With:    SIGNALHIRE_API_KEY=your_actual_key"
echo ""

if [ "$GLOBAL_INSTALL" = true ]; then
    echo "3. Test the installation:"
    echo "   signalhire-agent doctor"
    echo ""
    echo "4. Start searching for prospects:"
    echo "   signalhire-agent search --help"
    echo "   signalhire-agent search --title 'Software Engineer' --location 'San Francisco'"
    echo ""
    echo "5. Get help anytime:"
    echo "   signalhire-agent --help"
    echo ""
    echo "🎉 You can now run 'signalhire-agent' from anywhere!"
    echo ""
    echo "Note: If 'signalhire-agent' command doesn't work immediately:"
    echo "  - Restart your terminal, or"
    echo "  - Run: source ~/.bashrc"
else
    echo "2. Test the installation:"
    echo "   ./signalhire-agent doctor"
    echo ""
    echo "3. Start searching for prospects:"
    echo "   ./signalhire-agent search --help"
    echo "   ./signalhire-agent search --title 'Software Engineer' --location 'San Francisco'"
    echo ""
    echo "4. Get help anytime:"
    echo "   ./signalhire-agent --help"
    echo ""
    echo "Note: Use ./signalhire-agent (requires being in project directory)"
fi