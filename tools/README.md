# Tools Directory

This directory contains utility scripts and development tools.

## Structure

- **data-processing/** - Scripts for data manipulation and conversion
  - `check_existing_contacts.py` - Check for duplicate contacts
  - `convert_to_csv.py` - Convert data formats to CSV
  - `create_test_sample.py` - Generate test data samples

- **testing/** - Testing utilities and example scripts
  - `example_bulk_reveal.py` - Example bulk reveal operations
  - `test_reveal_api.py` - API testing scripts
  - `simple_callback_server.py` - Simple webhook/callback server
  - `run_tests.py` - Test runner utility

- **development/** - Development and build tools
  - `run.py` - Main development runner script
  - `setup.py` - Package installation script
  - `docker-compose.yml` - Multi-container development setup
  - `Dockerfile` - Container build configuration

## Usage

Run scripts from the project root directory:

```bash
# Data processing
python tools/data-processing/convert_to_csv.py input.json

# Testing
python tools/testing/test_reveal_api.py

# Development
python tools/development/run.py -m pytest
```