"""
Claude Code SDK Intelligent Validator
Provides intelligent validation and auto-correction for search queries and data.
"""

from typing import Any, Dict, List, Tuple
from claude_code_sdk import tool, create_sdk_mcp_server

# Import existing validation utilities
from ..lib.validation import (
    ValidationResult,
    validate_email,
    validate_phone,
    validate_signalhire_uid,
)


@tool("validate_and_fix_search", "Intelligently validate and fix search queries", {
    "query": str,
    "field_name": str
})
async def validate_and_fix_search(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Intelligently validate and fix Boolean search queries.

    This tool goes beyond basic validation to actually fix common issues:
    - Unbalanced parentheses
    - Incorrect operator placement
    - Case sensitivity issues
    - Adjacent operators
    """
    query = args.get("query", "")
    field_name = args.get("field_name", "Query")

    if not query:
        return {
            "content": [{
                "type": "text",
                "text": f"✅ {field_name} is empty (optional field)"
            }]
        }

    fixed_query = query
    fixes_applied = []

    # Fix 1: Uppercase Boolean operators
    for op in ['and', 'or', 'not']:
        if f' {op} ' in fixed_query.lower():
            fixed_query = fixed_query.replace(f' {op} ', f' {op.upper()} ')
            fixes_applied.append(f"Uppercased {op} operator")

    # Fix 2: Balance parentheses
    open_count = fixed_query.count('(')
    close_count = fixed_query.count(')')

    if open_count > close_count:
        fixed_query += ')' * (open_count - close_count)
        fixes_applied.append(f"Added {open_count - close_count} closing parentheses")
    elif close_count > open_count:
        fixed_query = '(' * (close_count - open_count) + fixed_query
        fixes_applied.append(f"Added {close_count - open_count} opening parentheses")

    # Fix 3: Remove trailing operators
    words = fixed_query.split()
    if words and words[-1] in ['AND', 'OR', 'NOT']:
        fixed_query = ' '.join(words[:-1])
        fixes_applied.append(f"Removed trailing {words[-1]} operator")

    # Fix 4: Fix adjacent operators
    fixed_query = fixed_query.replace(' AND AND ', ' AND ')
    fixed_query = fixed_query.replace(' OR OR ', ' OR ')
    fixed_query = fixed_query.replace(' AND OR ', ' AND ')
    fixed_query = fixed_query.replace(' OR AND ', ' OR ')

    # Fix 5: Remove leading AND/OR
    if fixed_query.startswith('AND '):
        fixed_query = fixed_query[4:]
        fixes_applied.append("Removed leading AND")
    elif fixed_query.startswith('OR '):
        fixed_query = fixed_query[3:]
        fixes_applied.append("Removed leading OR")

    result_text = f"✅ Fixed {field_name}:\n"
    result_text += f"Original: {query}\n"
    result_text += f"Fixed: {fixed_query}\n"

    if fixes_applied:
        result_text += "\nFixes applied:\n"
        for fix in fixes_applied:
            result_text += f"• {fix}\n"
    else:
        result_text = f"✅ {field_name} is valid - no fixes needed"

    return {
        "content": [{
            "type": "text",
            "text": result_text
        }],
        "fixed_query": fixed_query,
        "is_valid": True,
        "fixes_applied": fixes_applied
    }


@tool("validate_and_fix_location", "Parse and validate location strings", {
    "location": str
})
async def validate_and_fix_location(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Intelligently parse location strings into components.

    Handles various formats:
    - "Toronto, Ontario, Canada"
    - "Toronto, ON"
    - "San Francisco Bay Area"
    - "Remote"
    """
    location = args.get("location", "")

    if not location:
        return {
            "content": [{
                "type": "text",
                "text": "❌ No location provided"
            }]
        }

    # Common patterns and fixes
    location_patterns = {
        # Canadian provinces
        ", ON": ", Ontario, Canada",
        ", BC": ", British Columbia, Canada",
        ", AB": ", Alberta, Canada",
        ", QC": ", Quebec, Canada",
        # US states
        ", CA": ", California, USA",
        ", NY": ", New York, USA",
        ", TX": ", Texas, USA",
        # Special cases
        "Bay Area": "San Francisco Bay Area, California, USA",
        "GTA": "Greater Toronto Area, Ontario, Canada",
        "Remote": "Remote, Remote, Remote"
    }

    fixed_location = location
    for pattern, replacement in location_patterns.items():
        if pattern in fixed_location and ", Canada" not in fixed_location and ", USA" not in fixed_location:
            fixed_location = fixed_location.replace(pattern, replacement)

    # Parse into components
    parts = [p.strip() for p in fixed_location.split(',')]

    city = parts[0] if len(parts) > 0 else ""
    province_state = parts[1] if len(parts) > 1 else ""
    country = parts[2] if len(parts) > 2 else ""

    # Guess country if missing
    if not country:
        if any(prov in province_state for prov in ["Ontario", "British Columbia", "Alberta", "Quebec"]):
            country = "Canada"
        elif any(state in province_state for state in ["California", "New York", "Texas"]):
            country = "USA"

    result = {
        "content": [{
            "type": "text",
            "text": f"✅ Parsed location:\nCity: {city}\nProvince/State: {province_state}\nCountry: {country}"
        }],
        "city": city,
        "province_state": province_state,
        "country": country,
        "normalized": f"{city}, {province_state}, {country}".strip(", ")
    }

    return result


@tool("validate_and_clean_contact", "Validate and clean contact information", {
    "email": str,
    "phone": str
})
async def validate_and_clean_contact(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and clean email and phone data.

    Fixes common issues:
    - Email typos
    - Phone formatting
    - Invalid characters
    """
    email = args.get("email", "")
    phone = args.get("phone", "")

    results = []
    cleaned_data = {}

    # Validate and clean email
    if email:
        # Common email fixes
        email_fixed = email.lower().strip()
        email_fixed = email_fixed.replace("@gmail,com", "@gmail.com")
        email_fixed = email_fixed.replace("@gmial.com", "@gmail.com")
        email_fixed = email_fixed.replace("@yaho.com", "@yahoo.com")
        email_fixed = email_fixed.replace(" at ", "@")
        email_fixed = email_fixed.replace(" dot ", ".")

        result = validate_email(email_fixed)
        if result.is_valid:
            results.append(f"✅ Email valid: {result.cleaned_value}")
            cleaned_data["email"] = result.cleaned_value
        else:
            results.append(f"❌ Email invalid: {email} - {result.error_message}")

    # Validate and clean phone
    if phone:
        # Common phone fixes
        phone_fixed = phone.strip()
        # Remove common non-numeric except + at start
        phone_fixed = phone_fixed.replace("-", "").replace(" ", "")
        phone_fixed = phone_fixed.replace("(", "").replace(")", "")
        phone_fixed = phone_fixed.replace(".", "")

        # Add + if missing for international
        if phone_fixed and phone_fixed[0].isdigit() and len(phone_fixed) > 10:
            phone_fixed = "+" + phone_fixed

        result = validate_phone(phone_fixed)
        if result.is_valid:
            results.append(f"✅ Phone valid: {result.cleaned_value}")
            cleaned_data["phone"] = result.cleaned_value
        else:
            results.append(f"❌ Phone invalid: {phone} - {result.error_message}")

    return {
        "content": [{
            "type": "text",
            "text": "\n".join(results) if results else "No contact data provided"
        }],
        "cleaned_data": cleaned_data
    }


@tool("suggest_search_improvements", "Suggest improvements for search queries", {
    "title": str,
    "keywords": str,
    "target_role": str
})
async def suggest_search_improvements(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Suggest improvements for search queries based on target role.

    Provides intelligent suggestions for:
    - Heavy Equipment Technicians
    - Software Engineers
    - Sales Representatives
    - etc.
    """
    title = args.get("title", "")
    keywords = args.get("keywords", "")
    target_role = args.get("target_role", "general")

    suggestions = []

    if "heavy equipment" in target_role.lower() or "mechanic" in target_role.lower():
        # Heavy Equipment specific suggestions
        if not title:
            title = "(Heavy Equipment Technician) OR (Heavy Equipment Mechanic) OR (Heavy Duty Mechanic)"
            suggestions.append("Added comprehensive heavy equipment title search")

        if not keywords:
            keywords = "(technician OR mechanic OR maintenance OR repair) NOT (operator OR driver OR supervisor)"
            suggestions.append("Added keywords to exclude operators and focus on technicians")
        elif "NOT" not in keywords:
            keywords += " NOT (operator OR driver)"
            suggestions.append("Added exclusion for operators/drivers")

        # Check for brand names
        brands = ["CAT", "Caterpillar", "Komatsu", "John Deere", "Volvo", "Hitachi"]
        if not any(brand in keywords for brand in brands):
            suggestions.append("Consider adding equipment brands: " + ", ".join(brands[:3]))

    elif "software" in target_role.lower() or "engineer" in target_role.lower():
        # Software Engineer specific suggestions
        if not title:
            title = "(Software Engineer) OR (Software Developer) OR (Full Stack Developer)"
            suggestions.append("Added comprehensive software engineering titles")

        if not keywords:
            keywords = "(Python OR JavaScript OR Java) AND (API OR backend OR frontend)"
            suggestions.append("Added programming languages and technical keywords")

    result_text = "📝 Search Query Suggestions:\n\n"

    if suggestions:
        result_text += "Improvements made:\n"
        for suggestion in suggestions:
            result_text += f"• {suggestion}\n"
        result_text += f"\n"

    result_text += f"Optimized Title: {title or 'No title specified'}\n"
    result_text += f"Optimized Keywords: {keywords or 'No keywords specified'}\n"

    return {
        "content": [{
            "type": "text",
            "text": result_text
        }],
        "optimized_title": title,
        "optimized_keywords": keywords,
        "suggestions": suggestions
    }


# Create the SDK MCP server
intelligent_validator_server = create_sdk_mcp_server(
    name="intelligent-validator",
    version="1.0.0",
    tools=[
        validate_and_fix_search,
        validate_and_fix_location,
        validate_and_clean_contact,
        suggest_search_improvements
    ]
)


def get_intelligent_validator():
    """Get the intelligent validator server instance."""
    return intelligent_validator_server