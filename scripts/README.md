# Simple Scripts

Three simple scripts for solo development:

## 🔨 `./scripts/build.sh`
- Install dependencies
- Lint and fix code  
- Type check
- Test imports

## 🧪 `./scripts/test.sh` 
- Run unit tests
- Run integration tests
- Generate coverage report

## 🚀 `./scripts/deploy.sh [major|minor|patch]`
- Run tests
- Create git tag with version bump
- Push to GitHub (triggers release via GitHub Actions)

## Example Workflow

```bash
# Daily development
git add .
git commit -m "feat: add awesome feature"

# When ready to test thoroughly  
./scripts/test.sh

# When ready to deploy
./scripts/deploy.sh minor  # Creates v1.2.0 tag and releases
```

That's it! Simple, effective, no complexity.

## Other Scripts

The subdirectories contain specialized scripts for development, data processing, and testing that you can use as needed, but the three main scripts above handle 90% of your workflow.