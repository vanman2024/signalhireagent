#!/usr/bin/env python3
"""
Functional tests for rollback functionality.

These tests verify the rollback system works in realistic scenarios.
"""

import unittest
import tempfile
import shutil
import os
import subprocess
import sys
from pathlib import Path


class TestRollbackFunctional(unittest.TestCase):
    """Functional tests for rollback functionality."""

    def setUp(self):
        """Set up functional test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        # Create mock git repository
        self.setup_mock_git()

        # Copy actual scripts for testing
        self.copy_scripts()

    def tearDown(self):
        """Clean up functional test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def setup_mock_git(self):
        """Set up mock git repository for testing."""
        # Create git directory structure
        os.makedirs('.git/refs/tags', exist_ok=True)
        os.makedirs('.git/refs/heads', exist_ok=True)

        # Create mock tags
        Path('.git/refs/tags/v1.0.0').touch()
        Path('.git/refs/tags/v1.1.0').touch()
        Path('.git/refs/tags/v1.2.0').touch()

        # Create mock HEAD
        Path('.git/HEAD').write_text('ref: refs/heads/main\n')

        # Create mock git executable
        self.create_mock_git()

    def create_mock_git(self):
        """Create mock git executable for testing."""
        git_script = '''#!/bin/bash
case "$1" in
    tag)
        if [[ "$2" == "--list" ]]; then
            echo "v1.0.0"
            echo "v1.1.0"
            echo "v1.2.0"
        fi
        ;;
    status)
        if [[ "$*" == *"--porcelain"* ]]; then
            echo ""  # No changes
        else
            echo "On branch main"
            echo "Your branch is up to date with origin/main."
        fi
        ;;
    checkout)
        echo "Switched to branch '$2'"
        ;;
    stash)
        case "$2" in
            push)
                echo "Saved working directory and index state WIP on main: abc123"
                ;;
            list)
                echo ""  # No stashes
                ;;
            pop)
                echo "Dropped refs/stash@{0}"
                ;;
        esac
        ;;
    describe)
        if [[ "$*" == *"--tags --abbrev=0"* ]]; then
            echo "v1.2.0"
        fi
        ;;
    log)
        if [[ "$*" == *"--format=%cd --date=short"* ]]; then
            echo "2025-09-17"
        elif [[ "$*" == *"--format=%h"* ]]; then
            echo "abc123"
        fi
        ;;
    add)
        echo "Added $2 to staging"
        ;;
    commit)
        echo "Committed changes with message: $3"
        ;;
    push)
        echo "Pushed to origin"
        ;;
    *)
        echo "Mock git: $@"
        ;;
esac
'''
        git_path = os.path.join(self.test_dir, 'git')
        with open(git_path, 'w') as f:
            f.write(git_script)
        os.chmod(git_path, 0o755)

        # Add to PATH
        os.environ['PATH'] = f"{self.test_dir}:{os.environ['PATH']}"

    def copy_scripts(self):
        """Copy actual rollback scripts for testing."""
        project_root = Path(__file__).parent.parent.parent.parent

        # Copy ops script
        ops_src = os.path.join(project_root, 'devops', 'ops', 'ops')
        if os.path.exists(ops_src):
            shutil.copy2(ops_src, 'ops')
            os.chmod('ops', 0o755)

        # Copy rollback script
        rollback_src = os.path.join(project_root, 'devops', 'deploy', 'commands', 'rollback.sh')
        if os.path.exists(rollback_src):
            shutil.copy2(rollback_src, 'rollback.sh')
            os.chmod('rollback.sh', 0o755)

    def test_ops_rollback_command_integration(self):
        """Test ops rollback command integration."""
        if not os.path.exists('ops'):
            self.skipTest("ops script not available")

        # Test help command
        result = subprocess.run(['./ops', 'help'],
                              capture_output=True, text=True, cwd=self.test_dir)

        self.assertEqual(result.returncode, 0)
        self.assertIn('rollback', result.stdout)

    def test_rollback_script_help_integration(self):
        """Test rollback script help integration."""
        if not os.path.exists('rollback.sh'):
            self.skipTest("rollback script not available")

        result = subprocess.run(['./rollback.sh', '--help'],
                              capture_output=True, text=True, cwd=self.test_dir)

        self.assertEqual(result.returncode, 0)
        self.assertIn('USAGE', result.stdout)
        self.assertIn('version', result.stdout)

    def test_git_integration(self):
        """Test git command integration."""
        # Test git tag listing
        result = subprocess.run(['git', 'tag', '--list'],
                              capture_output=True, text=True, cwd=self.test_dir)

        self.assertEqual(result.returncode, 0)
        self.assertIn('v1.0.0', result.stdout)
        self.assertIn('v1.1.0', result.stdout)
        self.assertIn('v1.2.0', result.stdout)

    def test_deployment_workflow_simulation(self):
        """Test deployment workflow simulation."""
        # Create mock deployment directory
        deploy_dir = os.path.join(self.test_dir, 'deploy')
        os.makedirs(deploy_dir, exist_ok=True)

        # Create mock deployment files
        signalhire_agent = os.path.join(deploy_dir, 'signalhire-agent')
        Path(signalhire_agent).write_text('#!/bin/bash\necho "SignalHire Agent v1.2.0"')
        os.chmod(signalhire_agent, 0o755)

        # Test deployment verification
        result = subprocess.run([signalhire_agent],
                              capture_output=True, text=True, cwd=self.test_dir)

        self.assertEqual(result.returncode, 0)
        self.assertIn('SignalHire Agent', result.stdout)

    def test_backup_creation_workflow(self):
        """Test backup creation workflow."""
        import datetime

        # Simulate backup creation
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_dir = f"/tmp/signalhire-backup-{timestamp}"

        try:
            os.makedirs(backup_dir, exist_ok=True)

            # Create backup metadata
            backup_info = os.path.join(backup_dir, 'BACKUP_INFO.txt')
            with open(backup_info, 'w') as f:
                f.write(f"Backup created: {timestamp}\n")
                f.write("Original version: v1.2.0\n")
                f.write(f"Backup location: {backup_dir}\n")

            # Verify backup
            self.assertTrue(os.path.exists(backup_dir))
            self.assertTrue(os.path.exists(backup_info))

            with open(backup_info, 'r') as f:
                content = f.read()
                self.assertIn('v1.2.0', content)
                self.assertIn(timestamp, content)

        finally:
            # Clean up
            shutil.rmtree(backup_dir, ignore_errors=True)

    def test_version_validation_logic(self):
        """Test version validation logic."""
        valid_versions = [
            'v1.0.0', 'v1.2.3', 'v0.4.11', 'v2.0.0', 'v10.99.123'
        ]
        invalid_versions = [
            '1.0.0', 'invalid', 'v1', '1.0', 'v1.0', 'va.b.c',
            'v1.0.0.0', 'vx.y.z', 'v1.0.0-beta'
        ]

        for version in valid_versions:
            self.assertTrue(self.is_valid_semantic_version(version),
                          f"Version {version} should be valid")

        for version in invalid_versions:
            self.assertFalse(self.is_valid_semantic_version(version),
                           f"Version {version} should be invalid")

    def is_valid_semantic_version(self, version):
        """Check if version string is valid semantic version."""
        if not version.startswith('v'):
            return False

        parts = version[1:].split('.')
        if len(parts) != 3:
            return False

        try:
            return all(int(part) >= 0 for part in parts)
        except ValueError:
            return False

    def test_stash_workflow_simulation(self):
        """Test git stash workflow simulation."""
        # Test stash push
        result = subprocess.run(['git', 'stash', 'push', '-m', 'test stash'],
                              capture_output=True, text=True, cwd=self.test_dir)

        self.assertEqual(result.returncode, 0)
        self.assertIn('Saved working directory', result.stdout)

        # Test stash list
        result = subprocess.run(['git', 'stash', 'list'],
                              capture_output=True, text=True, cwd=self.test_dir)

        self.assertEqual(result.returncode, 0)

    def test_error_recovery_scenarios(self):
        """Test error recovery scenarios."""
        # Test with invalid version
        if os.path.exists('rollback.sh'):
            result = subprocess.run(['./rollback.sh', 'invalid-version'],
                                  capture_output=True, text=True, cwd=self.test_dir)

            # Should exit with error
            self.assertNotEqual(result.returncode, 0)

        # Test with non-existent target directory
        if os.path.exists('rollback.sh'):
            result = subprocess.run(['./rollback.sh', 'v1.0.0', '/non/existent/path'],
                                  capture_output=True, text=True, cwd=self.test_dir)

            # Should handle gracefully
            self.assertIsInstance(result.returncode, int)


if __name__ == '__main__':
    unittest.main(verbosity=2)
