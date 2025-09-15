# SignalHire Agent Development Guide

## The Testing Challenge We Solved

We discovered that browser automation applications have complex dependency management; this project has transitioned to API-only mode to simplify development:

1. **Node.js + Python Dependencies**: Stagehand (Node) + Playwright (Python) 
2. **Browser Installation**: Chromium with specific versions
3. **Environment Differences**: WSL, Windows, Linux compatibility
4. **Unicode Issues**: Console encoding problems with emojis

## Docker-Based Development Solution

We've implemented a containerized approach that provides:

- ✅ Consistent environment across all systems
- ✅ API-only: no browser tooling required
- ✅ Proper dependency management
- ✅ No host system pollution
- ✅ Easy cleanup and reset

## Quick Start

### 1. Build the Development Environment
```bash
# Build the Docker container
docker-compose build

# Start the development environment  
docker-compose up -d signalhire-agent

# Enter the container for interactive development
docker-compose exec signalhire-agent bash
```

### 2. Run Tests
```bash
python3 run.py -m pytest tests/contract/test_api_client_enhanced.py -q
python3 run.py -m pytest tests/contract/test_cli_api_first.py -q
python3 run.py -m pytest tests/contract/test_csv_export_enhanced.py -q
```

### 3. Development Workflow
```bash
# Edit files on your host system (they're mounted as volumes)
# Test locally:
python3 run.py -m pytest -q

# View screenshots generated during tests:
ls -la test_screenshots/

# Check logs:
ls -la logs/
```

## Testing Architecture

### Layer 1: Environment Tests
- Dependency verification
- Network connectivity

### Layer 2: SignalHire Contract Tests  
- API client contracts
- CLI interface contracts
- CSV export contracts

### Layer 3: Integration Tests (Future)
- Real credential login
- Search functionality
- Contact revelation

### Layer 4: End-to-End Tests (Future)
- Full workflows
- Export functionality
- Credit management

## Directory Structure

```
signalhireagent/
├── Dockerfile                 # Container definition
├── docker-compose.yml         # Development orchestration  
├── testing_strategy.md        # Comprehensive testing guide
├── run.py                     # Python dependency manager
├── src/                       # Application source code
├── tests/                     # Test suites
├── screenshots/               # Debug screenshots
├── test_screenshots/          # Test screenshots
├── downloads/                 # Export downloads
└── logs/                      # Application logs
```

## Current Status

### ✅ What Works
- API-only environment with all dependencies
- Enhanced API client and CLI contract tests

### 🚧 In Progress  
- Real credential testing (API)
- Full workflow automation (API)

### 📋 Next Steps
1. **Credential Testing**: Implement safe testing with real SignalHire accounts (API)
2. **Full Automation**: Complete search → reveal → export workflows (API)

## Environment Variables

Set these in your `.env` file or Docker environment:

```bash
# SignalHire credentials (for testing)
SIGNALHIRE_API_KEY=your-test-api-key
```

## Docker Commands Reference

```bash
# Start development environment
docker-compose up -d

# Run tests
python3 run.py -m pytest -q

# View logs
docker-compose logs signalhire-agent

# Clean restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Clean up everything
docker-compose down -v
docker system prune -f
```

## Troubleshooting

### API Connectivity Issues
- Verify internet connectivity inside your environment: `curl -I https://api.signalhire.com`
- Check DNS resolution and proxies

### Network Issues
- Test basic connectivity: `curl -I https://signalhire.com`
- Check DNS resolution: `nslookup signalhire.com`
- Verify no corporate firewalls blocking

### Volume Mount Issues
- Ensure Docker has permission to mount your project directory
- Check file ownership: `ls -la` inside container
- Fix permissions if needed: `chmod -R 755 .`

## Integration with CI/CD

The Docker approach makes CI/CD simple:

```yaml
# GitHub Actions example
- name: Run Contract Tests (API)
  run: |
    python3 run.py -m pytest -q
```

## Future Enhancements

1. **Multi-Browser Support**: Firefox, Safari testing
2. **Parallel Testing**: Run tests across multiple containers
3. **Visual Regression**: Screenshot comparison testing
4. **Performance Testing**: Load testing SignalHire integration
5. **Monitoring**: Real-time test results dashboard

This Docker-based approach solves the dependency hell and provides a solid foundation for reliable browser automation testing.
