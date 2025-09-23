import subprocess
import os
from pathlib import Path

# Assuming a logger is passed in a context object, similar to the JS version.
# A proper logger can be implemented later as per the conversion guide.
class MockLogger:
    def info(self, msg):
        print(f"INFO: {msg}")
    def warn(self, msg):
        print(f"WARN: {msg}")
    def error(self, msg):
        print(f"ERROR: {msg}")

def _execute_git_command(args, cwd=None):
    """Executes a git command and returns the result."""
    if cwd is None:
        cwd = Path.cwd()
    try:
        result = subprocess.run(
            ['git'] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False  # We check the status manually
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "status": result.returncode
        }
    except FileNotFoundError:
        return {
            "success": False,
            "stdout": "",
            "stderr": "Git command not found. Is Git installed and in your PATH?",
            "status": -1
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "status": -1
        }

def get_current_branch(context):
    """Gets the current Git branch name."""
    logger = context.get('logger', MockLogger())
    result = _execute_git_command(['branch', '--show-current'])
    if result["success"]:
        return result["stdout"]
    else:
        logger.warn(f"Failed to get current branch: {result['stderr']}")
        return None

def branch_exists(branch_name, context):
    """Checks if a branch exists locally."""
    logger = context.get('logger', MockLogger())
    result = _execute_git_command(['show-ref', '--verify', '--quiet', f"refs/heads/{branch_name}"])
    return result["success"]

def get_pr_number(branch_name, context):
    """Gets the PR number for a given branch using the GitHub CLI."""
    logger = context.get('logger', MockLogger())
    branch = branch_name or get_current_branch(context)
    if not branch:
        logger.warn("Could not determine branch name for PR lookup")
        return None
    try:
        result = subprocess.run(
            ['gh', 'pr', 'list', '--head', branch, '--json', 'number', '--jq', '.[0].number'],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        else:
            logger.warn(f"Failed to get PR number: {result.stderr or 'No PR found'}")
            return None
    except FileNotFoundError:
        logger.error("GitHub CLI (gh) not found. Is it installed and in your PATH?")
        return None
    except Exception as e:
        logger.error(f"Error getting PR number: {e}")
        return None

def is_working_directory_clean(context):
    """Checks if the Git working directory is clean."""
    logger = context.get('logger', MockLogger())
    result = _execute_git_command(['status', '--porcelain'])
    if result["success"]:
        return result["stdout"] == ''
    else:
        logger.warn(f"Failed to check working directory status: {result['stderr']}")
        return False

def get_changed_files(context):
    """Gets a list of changed files since the last commit."""
    logger = context.get('logger', MockLogger())
    result = _execute_git_command(['diff', '--name-only', 'HEAD'])
    if result["success"]:
        return result["stdout"].split('\n') if result["stdout"] else []
    else:
        logger.warn(f"Failed to get changed files: {result['stderr']}")
        return []

def safe_commit(message, context):
    """Stages all changes and commits them with the given message."""
    logger = context.get('logger', MockLogger())
    if is_working_directory_clean(context):
        logger.info("Working directory is clean, nothing to commit")
        return False

    add_result = _execute_git_command(['add', '-A'])
    if not add_result["success"]:
        logger.error(f"Failed to add files: {add_result['stderr']}")
        return False

    commit_result = _execute_git_command(['commit', '-m', message, '--no-verify'])
    if commit_result["success"]:
        logger.info(f"Successfully committed with message: {message}")
        return True
    else:
        logger.error(f"Failed to commit: {commit_result['stderr']}")
        return False

def safe_push(branch_name, context):
    """Pushes the specified or current branch to the origin."""
    logger = context.get('logger', MockLogger())
    branch = branch_name or get_current_branch(context)
    if not branch:
        logger.error("Could not determine branch name for push")
        return False

    result = _execute_git_command(['push', 'origin', branch, '--no-verify'])
    if result["success"]:
        logger.info(f"Successfully pushed branch: {branch}")
        return True
    else:
        logger.error(f"Failed to push branch {branch}: {result['stderr']}")
        return False

def create_branch_from_main(new_branch, main_branch='main', context=None):
    """Creates and checks out a new branch from the main branch after pulling the latest changes."""
    if context is None:
        context = {}
    logger = context.get('logger', MockLogger())

    # Checkout main branch
    result = _execute_git_command(['checkout', main_branch])
    if not result["success"]:
        logger.error(f"Failed to checkout {main_branch}: {result['stderr']}")
        return False

    # Pull latest changes
    result = _execute_git_command(['pull', 'origin', main_branch])
    if not result["success"]:
        logger.warn(f"Failed to pull {main_branch}: {result['stderr']}. Continuing anyway.")

    # Create and checkout new branch
    result = _execute_git_command(['checkout', '-b', new_branch])
    if result["success"]:
        logger.info(f"Successfully created and checked out branch: {new_branch}")
        return True
    else:
        logger.error(f"Failed to create branch {new_branch}: {result['stderr']}")
        return False

def get_repo_info(context):
    """Gets the repository owner and name from the git remote URL."""
    logger = context.get('logger', MockLogger())
    result = _execute_git_command(['remote', 'get-url', 'origin'])
    if result["success"] and result["stdout"]:
        remote_url = result["stdout"]
        # Basic parsing for GitHub URLs (SSH or HTTPS)
        match = re.search(r'github\.com[:/]([^/]+)/([^/.]+)', remote_url)
        if match:
            return f"{match.group(1)}/{match.group(2)}"
    logger.error(f"Could not determine repo info. Stderr: {result['stderr']}")
    return None

def push_bypass(branch_name, context):
    """Pushes the branch without running verification hooks."""
    logger = context.get('logger', MockLogger())
    branch = branch_name or get_current_branch(context)
    if not branch:
        logger.error("Could not determine branch name for push bypass")
        return False

    result = _execute_git_command(['push', '--no-verify', 'origin', branch])
    if result["success"]:
        logger.info(f"Successfully pushed branch {branch} with bypass")
        return True
    else:
        logger.error(f"Failed to push branch {branch} with bypass: {result['stderr']}")
        return False


# Orchestrator integration

def detect(context):
    return True


def deploy(context):
    if context.get('dry_run'):
        return {'status': 'skipped:dry-run'}
    context['logger'].info('Git helper utilities available')
    return {'status': 'ok'}
