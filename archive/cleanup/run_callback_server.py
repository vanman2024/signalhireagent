#!/usr/bin/env python3
"""
Run SignalHire callback server on port 8000.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lib.callback_server import CallbackServer
from services.complete_airtable_automation import CompleteAirtableAutomation

# Load environment variables
load_dotenv()

async def main():
    print("🚀 Starting SignalHire callback server on port 8000...")
    
    # Create callback server
    server = CallbackServer(host="0.0.0.0", port=8000)
    
    # Initialize automation for webhook handling
    automation = CompleteAirtableAutomation()
    
    # Register the webhook handler
    server.register_handler("airtable_webhook", automation.process_webhook)
    
    # Create the FastAPI app
    server.create_app()
    
    print(f"📡 Callback URL: http://localhost:8000/signalhire/callback")
    print("🎯 Registered handlers: airtable_webhook")
    print("✅ Server ready to receive SignalHire callbacks")
    
    # Start server (blocking)
    server.start(background=False)

if __name__ == "__main__":
    asyncio.run(main())