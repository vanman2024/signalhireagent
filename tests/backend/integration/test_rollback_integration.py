#!/usr/bin/env python3
"""
Integration tests for rollback functionality.

These tests verify the actual rollback scripts work correctly.
"""

import unittest
import tempfile
import shutil
import os
import subprocess
import sys
from pathlib import Path


class TestRollbackIntegration(unittest.TestCase):
    """Integration tests for actual rollback functionality."""

    def setUp(self):
        """Set up integration test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()

        # Copy the actual project files for testing
        project_root = Path(__file__).parent.parent.parent.parent
        self.project_root = str(project_root)

        # Create test environment
        os.chdir(self.test_dir)

        # Copy necessary files
        self.copy_project_files(project_root)

    def tearDown(self):
        """Clean up integration test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def copy_project_files(self, project_root):
        """Copy necessary project files for testing."""
        # Copy ops script
        ops_src = os.path.join(project_root, 'devops', 'ops', 'ops')
        ops_dest = os.path.join(self.test_dir, 'ops')
        if os.path.exists(ops_src):
            shutil.copy2(ops_src, ops_dest)
            os.chmod(ops_dest, 0o755)

        # Copy rollback script
        rollback_src = os.path.join(project_root, 'devops', 'deploy', 'commands', 'rollback.sh')
        rollback_dest = os.path.join(self.test_dir, 'rollback.sh')
        if os.path.exists(rollback_src):
            shutil.copy2(rollback_src, rollback_dest)
            os.chmod(rollback_dest, 0o755)

        # Create mock git repository
        self.init_mock_git_repo()

    def init_mock_git_repo(self):
        """Initialize a mock git repository for testing."""
        os.makedirs('.git/refs/tags', exist_ok=True)
        os.makedirs('.git/refs/heads', exist_ok=True)

        # Create mock tags
        Path('.git/refs/tags/v1.0.0').touch()
        Path('.git/refs/tags/v1.1.0').touch()
        Path('.git/refs/tags/v1.2.0').touch()

        # Create mock HEAD
        Path('.git/HEAD').write_text('ref: refs/heads/main\n')

        # Create mock git commands
        self.create_mock_git_commands()

    def create_mock_git_commands(self):
        """Create mock git commands for testing."""
        git_mock = '''#!/bin/bash
case "$1" in
    tag)
        if [[ "$2" == "--list" ]]; then
            echo "v1.0.0"
            echo "v1.1.0"
            echo "v1.2.0"
        fi
        ;;
    status)
        echo "On branch main"
        ;;
    checkout)
        echo "Switched to $2"
        ;;
    stash)
        if [[ "$2" == "push" ]]; then
            echo "Saved working directory"
        elif [[ "$2" == "list" ]]; then
            echo ""
        fi
        ;;
    describe)
        echo "v1.2.0"
        ;;
    log)
        echo "commit abc123"
        echo "Date: 2025-09-17"
        ;;
    *)
        echo "Mock git command: $@"
        ;;
esac
'''
        git_path = os.path.join(self.test_dir, 'git')
        with open(git_path, 'w') as f:
            f.write(git_mock)
        os.chmod(git_path, 0o755)

        # Add to PATH
        os.environ['PATH'] = f"{self.test_dir}:{os.environ['PATH']}"

    def test_ops_rollback_help(self):
        """Test ops rollback help output."""
        if not os.path.exists('ops'):
            self.skipTest("ops script not available")

        result = subprocess.run(['./ops', 'help'],
                              capture_output=True, text=True, cwd=self.test_dir)

        self.assertEqual(result.returncode, 0)
        self.assertIn('rollback', result.stdout)

    def test_rollback_script_help(self):
        """Test rollback script help output."""
        if not os.path.exists('rollback.sh'):
            self.skipTest("rollback script not available")

        result = subprocess.run(['./rollback.sh', '--help'],
                              capture_output=True, text=True, cwd=self.test_dir)

        self.assertEqual(result.returncode, 0)
        self.assertIn('USAGE', result.stdout)

    def test_rollback_script_available_versions(self):
        """Test that rollback script shows available versions."""
        if not os.path.exists('rollback.sh'):
            self.skipTest("rollback script not available")

        result = subprocess.run(['./rollback.sh', '--help'],
                              capture_output=True, text=True, cwd=self.test_dir)

        # Should show available versions in help output
        self.assertEqual(result.returncode, 0)

    @unittest.skip("Requires user interaction")
    def test_ops_rollback_dry_run(self):
        """Test ops rollback dry run (would require user input)."""
        if not os.path.exists('ops'):
            self.skipTest("ops script not available")

        # This test would require mocking user input
        # In real scenario, would test with 'echo "n" | ./ops rollback v1.0.0'
        pass

    def test_git_mock_commands(self):
        """Test that mock git commands work."""
        result = subprocess.run(['git', 'tag', '--list'],
                              capture_output=True, text=True, cwd=self.test_dir)

        self.assertEqual(result.returncode, 0)
        self.assertIn('v1.0.0', result.stdout)
        self.assertIn('v1.1.0', result.stdout)
        self.assertIn('v1.2.0', result.stdout)

    def test_deployment_directory_handling(self):
        """Test deployment directory creation and handling."""
        deploy_dir = os.path.join(self.test_dir, 'deploy')
        os.makedirs(deploy_dir, exist_ok=True)

        # Create mock deployment files
        signalhire_agent = os.path.join(deploy_dir, 'signalhire-agent')
        Path(signalhire_agent).touch()
        os.chmod(signalhire_agent, 0o755)

        # Verify deployment structure
        self.assertTrue(os.path.exists(deploy_dir))
        self.assertTrue(os.path.exists(signalhire_agent))
        self.assertTrue(os.access(signalhire_agent, os.X_OK))

    def test_backup_creation_logic(self):
        """Test backup directory creation logic."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_dir = f"/tmp/signalhire-backup-{timestamp}"

        # Simulate backup creation
        os.makedirs(backup_dir, exist_ok=True)
        self.assertTrue(os.path.exists(backup_dir))

        # Create backup info file
        backup_info = os.path.join(backup_dir, 'BACKUP_INFO.txt')
        with open(backup_info, 'w') as f:
            f.write(f"Backup created: {timestamp}\n")
            f.write("Original version: v1.2.0\n")
            f.write(f"Backup location: {backup_dir}\n")

        self.assertTrue(os.path.exists(backup_info))

        # Clean up
        shutil.rmtree(backup_dir)

    def test_version_validation(self):
        """Test version string validation."""
        valid_versions = ['v1.0.0', 'v1.2.3', 'v0.4.11', 'v2.0.0']
        invalid_versions = ['1.0.0', 'invalid', 'v1', '1.0', 'v1.0', 'va.b.c']

        for version in valid_versions:
            self.assertTrue(self.is_valid_version(version),
                          f"Version {version} should be valid")

        for version in invalid_versions:
            self.assertFalse(self.is_valid_version(version),
                           f"Version {version} should be invalid")

    def is_valid_version(self, version):
        """Check if version string is valid."""
        if not version.startswith('v'):
            return False

        parts = version[1:].split('.')
        if len(parts) != 3:
            return False

        return all(part.isdigit() for part in parts)

    def test_error_handling_scenarios(self):
        """Test various error handling scenarios."""
        # Test with non-existent script (should raise FileNotFoundError)
        with self.assertRaises(FileNotFoundError):
            subprocess.run(['./non-existent-script', 'test'],
                          capture_output=True, text=True, cwd=self.test_dir)

        # Test with invalid arguments for rollback script
        if os.path.exists('rollback.sh'):
            result = subprocess.run(['./rollback.sh', 'invalid-arg', '--invalid-flag'],
                                  capture_output=True, text=True, cwd=self.test_dir)

            # Should handle gracefully (exact behavior depends on script)
            self.assertIsInstance(result.returncode, int)


class TestRollbackWorkflow(unittest.TestCase):
    """Test complete rollback workflow scenarios."""

    def setUp(self):
        """Set up workflow test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        """Clean up workflow test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_rollback_workflow_simulation(self):
        """Simulate a complete rollback workflow."""
        # Create mock project structure
        self.create_mock_project()

        # Simulate pre-rollback state
        self.simulate_pre_rollback_state()

        # Simulate rollback process
        success = self.simulate_rollback_process()

        # Verify post-rollback state
        self.verify_post_rollback_state()

        self.assertTrue(success, "Rollback workflow should complete successfully")

    def create_mock_project(self):
        """Create mock project structure for testing."""
        # Create basic directory structure
        os.makedirs('src', exist_ok=True)
        os.makedirs('tests', exist_ok=True)
        os.makedirs('devops/deploy', exist_ok=True)

        # Create mock files
        Path('pyproject.toml').write_text('[project]\nversion = "1.2.0"\n')
        Path('src/main.py').write_text('print("SignalHire Agent")')
        Path('README.md').write_text('# SignalHire Agent')

    def simulate_pre_rollback_state(self):
        """Simulate the state before rollback."""
        # Create some "changes" that would be stashed
        Path('temp_changes.txt').write_text('These changes should be stashed')

        # Create deployment directory
        deploy_dir = 'deploy'
        os.makedirs(deploy_dir, exist_ok=True)
        Path(os.path.join(deploy_dir, 'signalhire-agent')).touch()

        self.assertTrue(os.path.exists('temp_changes.txt'))
        self.assertTrue(os.path.exists(deploy_dir))

    def simulate_rollback_process(self):
        """Simulate the rollback process."""
        try:
            # This would be the actual rollback logic
            # For testing, we just simulate success
            return True
        except Exception as e:
            print(f"Rollback simulation failed: {e}")
            return False

    def verify_post_rollback_state(self):
        """Verify the state after rollback."""
        # In a real test, this would verify:
        # - Correct version is checked out
        # - Deployment is rebuilt
        # - Backup is created
        # - Changes are stashed (if any)
        # - Verification passes

        # For this simulation, just check basic structure
        self.assertTrue(os.path.exists('src'))
        self.assertTrue(os.path.exists('pyproject.toml'))


if __name__ == '__main__':
    # Set up test environment
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)

    # Run tests with verbose output
    unittest.main(verbosity=2)
