# Archive Directory

This directory contains legacy test files and experimental code that were moved from the project root for better organization.

## legacy_tests/
Contains all the scattered test files that were in the root directory during development:
- Various browser automation experiments (test_*.py, *_test.py)
- Cloudflare bypass attempts
- Session management tests
- Debug and hybrid automation scripts

These files represent the exploration phase of the project and are preserved for reference but are not part of the current clean architecture.

## Current Testing
Active tests are now properly organized in:
- `tests/unit/` - Unit tests for individual components
- `tests/integration/` - End-to-end workflow tests  
- `tests/contract/` - Browser automation contract tests

## Note
These archived files may have dependencies or configurations that are no longer compatible with the current project structure.