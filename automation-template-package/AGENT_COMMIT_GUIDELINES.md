# 🤖 Agent Commit Guidelines

**Smart commit discipline for AI agents to prevent spam releases and maintain quality.**

## 🎯 **Core Principle**

**Commit frequently, release strategically**
- ✅ Make commits during development (no release pressure)  
- ✅ Release evaluation happens every ~10 commits
- ✅ Quality checks only run when considering releases

## 📝 **Commit Patterns for Agents**

### **Development Commits** (Most Common)
```bash
# Work-in-progress commits (no release triggered)
git commit -m "wip: implementing search feature"
git commit -m "dev: add validation logic" 
git commit -m "update: refine error handling"
git commit -m "temp: testing new approach"
```

### **Milestone Commits** (Release Eligible)  
```bash
# Use these when work is complete and tested
git commit -m "feat: add comprehensive search filtering"
git commit -m "fix: resolve memory leak in data processing"
git commit -m "feat!: new API structure (BREAKING)"
```

## 🔄 **Smart Release Logic**

### **Every Commit**:
- ✅ Auto-sync to deployment targets (fast)
- ❌ NO release evaluation (prevents spam)

### **Every 10+ Commits**:
- 🔍 Evaluate accumulated changes for release worthiness
- 🧪 Run quality checks (linting, imports, smoke tests)  
- 🎯 Suggest release only if changes are significant

### **Release Criteria**:
- **Major**: Contains `BREAKING` or `!` in any commit
- **Minor**: Has `feat:` commits + good significance score
- **Patch**: Has `fix:` commits or accumulated improvements
- **None**: Changes not significant enough yet

## 🛡️ **Quality Gates** (Only at Release Time)

```bash
# Lightweight checks that don't block development:
✓ Code linting (warnings OK, errors block)
✓ Import validation (can code be imported?)  
✓ Smoke test (does CLI --help work?)
✓ 70% pass rate required for release
```

## 🎮 **Agent Best Practices**

### **During Active Development**
```bash
# Frequent commits with development prefixes
git commit -m "dev: add user input validation"
git commit -m "wip: implementing API client"
git commit -m "update: improve error messages"
```

### **When Feature is Complete**
```bash
# Single milestone commit
git commit -m "feat: complete user authentication system

- Add login/logout functionality
- Implement session management  
- Add password validation
- Include comprehensive tests"
```

### **When Fixing Issues**
```bash
git commit -m "fix: resolve authentication token expiry bug

- Update token refresh logic
- Add proper error handling
- Include regression test"
```

## 🚨 **What This Prevents**

❌ **Release spam**: No more releases for every tiny commit  
❌ **Broken releases**: Quality checks catch major issues  
❌ **Agent conflicts**: Clear commit patterns reduce confusion  
❌ **Development blocking**: Quality checks only at release time

## ✅ **What This Enables**

✅ **Rapid development**: Commit freely without release pressure  
✅ **Quality releases**: Only significant, tested changes get released  
✅ **Clear intent**: Commit prefixes show development vs milestone work  
✅ **Team coordination**: Agents can see development progress

## 🔧 **Commands for Agents**

```bash
# Check if release evaluation is due
./scripts/build/smart-release-evaluator.sh --force-check

# See current commit count since last release  
git rev-list --count $(git describe --tags --abbrev=0)..HEAD

# Check automation status
./scripts/build/continuous-deployment.sh status
```

## 📊 **Example Workflow**

```bash
# Day 1-2: Development commits
git commit -m "dev: start implementing feature X"
git commit -m "wip: add data models"  
git commit -m "update: refine validation logic"
# → Auto-sync happens, no release evaluation

# Day 3: Feature complete  
git commit -m "feat: complete feature X with full validation"
# → If 10+ commits accumulated, runs evaluation
# → Quality checks run, release created if passed

# Continue development...
git commit -m "dev: start feature Y"
```

## 🎯 **Result**

- **Developers work freely** without quality gate friction
- **Releases are meaningful** and tested
- **Deployment stays current** via auto-sync
- **Quality is maintained** without blocking development

**Perfect balance of speed and quality!** 🚀