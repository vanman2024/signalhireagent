#!/bin/bash

echo "🚀 Setting up SignalHire Agent..."

# No complex installation needed - the launcher script handles everything
echo "✅ Using universal launcher (works on all systems)"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env configuration file..."
    cat > .env << 'EOF'
# SignalHire Agent Configuration
# Get your API key from SignalHire support
SIGNALHIRE_API_KEY=your_api_key_here

# Optional: Alternative authentication (choose one method)
# SIGNALHIRE_EMAIL=your@email.com
# SIGNALHIRE_PASSWORD=your_password

# Optional: API Configuration
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
echo "1. Edit .env file with your SignalHire API key:"
echo "   nano .env"
echo ""

echo "2. Test the installation:"
echo "   ./signalhire-agent doctor"
echo ""
echo "3. Start searching for prospects:"
echo "   ./signalhire-agent search --help"
echo "   ./signalhire-agent search --title 'Software Engineer' --location 'San Francisco'"
echo ""
echo "4. Get help anytime:"
echo "   ./signalhire-agent --help"