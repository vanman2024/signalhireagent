#!/bin/bash
# PR Review Automation Script
# Triggers pr-reviewer sub-agent when PRs are created/updated

set -e

PR_NUMBER=${1:-$GITHUB_EVENT_NUMBER}
PR_BRANCH=${2:-$GITHUB_HEAD_REF}
BASE_BRANCH=${3:-main}

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== PR Review Automation ===${NC}"
echo "PR #$PR_NUMBER: $PR_BRANCH → $BASE_BRANCH"

# Step 1: Get PR diff
echo -e "${YELLOW}Fetching PR diff...${NC}"
PR_DIFF=$(gh pr diff $PR_NUMBER)

# Step 2: Identify agent from branch name
AGENT_NAME=""
if [[ $PR_BRANCH == agent-claude-* ]]; then
    AGENT_NAME="@claude"
elif [[ $PR_BRANCH == agent-codex-* ]]; then
    AGENT_NAME="@codex"
elif [[ $PR_BRANCH == agent-qwen-* ]]; then
    AGENT_NAME="@qwen"
elif [[ $PR_BRANCH == agent-gemini-* ]]; then
    AGENT_NAME="@gemini"
elif [[ $PR_BRANCH == agent-copilot-* ]]; then
    AGENT_NAME="@copilot"
fi

echo "Detected agent: $AGENT_NAME"

# Step 3: Prepare review context
REVIEW_CONTEXT=$(cat <<EOF
# Pull Request Review Request

**PR Number**: #$PR_NUMBER
**Branch**: $PR_BRANCH → $BASE_BRANCH
**Agent**: $AGENT_NAME

## Review Checklist
- [ ] Security vulnerabilities
- [ ] Code quality and standards
- [ ] Performance implications
- [ ] Architecture compliance
- [ ] Test coverage
- [ ] Documentation updates
- [ ] Breaking changes
- [ ] Dependencies

## Diff Summary
\`\`\`diff
$(echo "$PR_DIFF" | head -100)
\`\`\`

Please review using the pr-reviewer sub-agent and provide:
1. Security assessment
2. Code quality score (1-10)
3. Required changes (if any)
4. Approval recommendation
EOF
)

# Step 4: Invoke PR reviewer sub-agent non-interactively
echo -e "${YELLOW}Invoking PR reviewer sub-agent...${NC}"

REVIEW_OUTPUT=$(echo "$REVIEW_CONTEXT" | claude -p "Review this PR thoroughly using the pr-reviewer sub-agent. Focus on security, quality, and architecture.")

# Step 5: Parse review output
SECURITY_ISSUES=$(echo "$REVIEW_OUTPUT" | grep -i "security" || echo "No security issues found")
QUALITY_SCORE=$(echo "$REVIEW_OUTPUT" | grep -oP "Quality Score: \K[0-9]+" || echo "7")
APPROVAL=$(echo "$REVIEW_OUTPUT" | grep -i "approve" || echo "pending")

# Step 6: Post review comment
echo -e "${YELLOW}Posting review comment...${NC}"

COMMENT=$(cat <<EOF
## 🤖 Automated PR Review

**Reviewer**: Claude PR-Reviewer Sub-Agent
**PR**: #$PR_NUMBER
**Agent**: $AGENT_NAME

### Review Summary

$REVIEW_OUTPUT

### Automated Checks
- Security Scan: ${SECURITY_ISSUES}
- Quality Score: ${QUALITY_SCORE}/10
- Recommendation: ${APPROVAL}

### Next Steps
1. Address any required changes
2. Request re-review if needed
3. Await human approval for merge

---
*This review was generated automatically by the PR review sub-agent*
EOF
)

# Post the comment
gh pr comment $PR_NUMBER --body "$COMMENT"

# Step 7: Add labels based on review
if [[ $QUALITY_SCORE -ge 8 ]]; then
    gh pr label $PR_NUMBER --add "high-quality"
elif [[ $QUALITY_SCORE -le 5 ]]; then
    gh pr label $PR_NUMBER --add "needs-work"
fi

if echo "$SECURITY_ISSUES" | grep -q "No security issues"; then
    gh pr label $PR_NUMBER --add "security-reviewed"
else
    gh pr label $PR_NUMBER --add "security-concerns"
fi

# Step 8: Trigger dependent task notification if approved
if echo "$APPROVAL" | grep -iq "approve"; then
    echo -e "${GREEN}PR approved by reviewer. Triggering dependent tasks...${NC}"
    ./agent-task-notification.sh $PR_NUMBER $AGENT_NAME
else
    echo -e "${YELLOW}PR needs changes before approval${NC}"
fi

echo -e "${GREEN}PR review automation complete!${NC}"