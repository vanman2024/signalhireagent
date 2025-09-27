#!/usr/bin/env python3
"""
True automated SignalHire to Airtable integration using Claude Code SDK.
This uses Claude to automatically handle the MCP tools and API integration.
"""

import asyncio
import os
import json
from pathlib import Path

# Try importing Claude Code SDK
try:
    from claude_code_sdk import query, ClaudeCodeOptions
except ImportError:
    print("Claude Code SDK not found. Please install with: pip install claude-code-sdk")
    exit(1)


async def main():
    """Use Claude Code SDK to automate the entire workflow."""
    
    print("Starting Claude-powered SignalHire to Airtable automation...")
    
    # Create the automation prompt for Claude
    automation_prompt = """
    Please automate the SignalHire to Airtable workflow:
    
    1. Read the cache file at /home/vanman2025/.signalhire-agent/cache/revealed_contacts.json
    2. Filter for heavy equipment professionals in Canada (exclude drivers, operators, sales, coordinators, supervisors)
    3. Check existing contacts in Airtable (base: appQoYINM992nBZ50, table: tbl0uFVaAfcNjT2rS) to avoid duplicates
    4. Create new records in Airtable for contacts that don't already exist
    
    For each contact, create an Airtable record with these fields:
    - SignalHire ID: the uid from the cache
    - First Name, Last Name, Full Name: parsed from profile.fullName
    - Job Title: from profile.experience[0].title
    - Company: from profile.experience[0].company  
    - Location: from profile.location
    - Primary Email, Phone Number, LinkedIn URL: from contacts array
    - SignalHire Profile: https://app.signalhire.com/profile/{uid}
    - Skills: join profile.skills with commas
    - Status: "New"
    - Date Added: current ISO timestamp
    - Source Search: "Cache - Heavy Equipment"
    
    Please complete this workflow and provide a summary.
    """
    
    # Configure Claude options with MCP
    options = ClaudeCodeOptions(
        mcp_servers=".mcp.json",  # Path to MCP configuration file
        allowed_tools=[
            "mcp__airtable__list_records",
            "mcp__airtable__create_record",
            "mcp__filesystem__read_text_file"
        ]
    )
    
    try:
        # Execute the automation workflow using Claude SDK
        async for message in query(
            prompt=automation_prompt,
            options=options
        ):
            message_type = message.get("type")
            message_subtype = message.get("subtype")
            
            if message_type == "text":
                print(f"Claude: {message['text']}")
            elif message_type == "result":
                if message_subtype == "success":
                    print(f"Tool Result: {message['result']}")
                elif message_subtype == "error":
                    print(f"Tool Error: {message['error']}")
            elif message_type == "system":
                if message_subtype == "init":
                    print("Claude SDK initialized successfully")
                    # Check MCP server status
                    mcp_servers = message.get("mcp_servers", [])
                    for server in mcp_servers:
                        name = server.get("name", "unknown")
                        status = server.get("status", "unknown")
                        print(f"  MCP Server '{name}': {status}")
                        
    except Exception as e:
        print(f"Error in automation: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())