import json
import hmac
import hashlib
import os
import secrets
from datetime import datetime
from pathlib import Path

import requests

class WebhookUpdateNotifier:
    """
    Sends notifications to deployed projects when template updates are available.
    """

    def __init__(self, registry_path=None):
        self.template_repo = 'vanman2024/multi-agent-claude-code'
        self.webhook_secret = os.getenv('TEMPLATE_WEBHOOK_SECRET', 'template-update-secret')
        if registry_path:
            self.registry_path = Path(registry_path)
        else:
            # Default path relative to this file's location
            self.registry_path = Path(__file__).parent / 'deployed-projects-registry.json'
        self.deployed_projects = self._load_project_registry()

    def add_project(self, config):
        """Adds a deployed project to receive update notifications."""
        project = {
            "id": config.get("id", secrets.token_hex(8)),
            "name": config["name"],
            "webhook_url": config["webhook_url"],
            "owner": config.get("owner"),
            "repo": config.get("repo"),
            "deployed_version": config.get("deployed_version"),
            "critical_updates_only": config.get("critical_updates_only", False),
            "auto_update": config.get("auto_update", False),
            "last_notified": None,
        }
        self.deployed_projects.append(project)
        self._save_project_registry()
        return project["id"]

    def remove_project(self, project_id):
        """Removes a project from update notifications."""
        self.deployed_projects = [p for p in self.deployed_projects if p["id"] != project_id]
        self._save_project_registry()

    def notify_projects(self, update_info):
        """Notifies all registered projects of template updates."""
        print(f"📢 Notifying {len(self.deployed_projects)} deployed projects of template updates...")
        results = {"successful": [], "failed": [], "skipped": []}

        for project in self.deployed_projects:
            try:
                if not self._should_notify_project(project, update_info):
                    results["skipped"].append({"project": project["name"], "reason": "No critical updates"})
                    continue

                notification_payload = self._create_notification_payload(project, update_info)

                if project.get("auto_update"):
                    self._trigger_auto_update(project, notification_payload)
                else:
                    self._send_webhook(project, notification_payload)

                project["last_notified"] = datetime.utcnow().isoformat()
                results["successful"].append(project["name"])
            except Exception as e:
                print(f"❌ Failed to notify {project['name']}: {e}")
                results["failed"].append({"project": project["name"], "error": str(e)})

        self._save_project_registry()
        print(f"✅ Notification complete: {len(results['successful'])} successful, {len(results['failed'])} failed, {len(results['skipped'])} skipped")
        return results

    def _should_notify_project(self, project, update_info):
        """Checks if a project should be notified of this update."""
        if project.get("deployed_version") == update_info.get("latest_version"):
            return False
        if project.get("critical_updates_only"):
            return any(
                change.get("priority") == "high" or
                "devops/" in change.get("path", "") or
                "agentswarm/" in change.get("path", "")
                for change in update_info.get("changes", [])
            )
        return True

    def _create_notification_payload(self, project, update_info):
        """Creates the notification payload for a project."""
        return {
            "event": "template_update_available",
            "timestamp": datetime.utcnow().isoformat(),
            "template": {
                "repository": self.template_repo,
                "current_version": update_info.get("current_version"),
                "latest_version": update_info.get("latest_version"),
                "update_url": f"https://github.com/{self.template_repo}/compare/{update_info.get('current_version')}...{update_info.get('latest_version')}",
            },
            "project": {
                "id": project.get("id"),
                "name": project.get("name"),
                "deployed_version": project.get("deployed_version"),
            },
            "updates": {
                "total": len(update_info.get("changes", [])),
                "critical": len([c for c in update_info.get("changes", []) if c.get("priority") == "high"]),
                "changes": update_info.get("changes", []),
            },
            "actions": {
                "check_command": "/update-from-template --check",
                "preview_command": "/update-from-template --preview",
                "update_command": "/update-from-template",
                "force_update_command": "/update-from-template --force",
            },
        }

    def _send_webhook(self, project, payload):
        """Sends a webhook notification to a project."""
        payload_bytes = json.dumps(payload).encode('utf-8')
        signature = self._create_webhook_signature(payload_bytes)
        headers = {
            'Content-Type': 'application/json',
            'X-Template-Signature': signature,
            'X-Template-Event': 'update_available',
            'User-Agent': 'Template-Update-Notifier/1.0',
        }
        try:
            response = requests.post(project["webhook_url"], data=payload_bytes, headers=headers, timeout=10)
            response.raise_for_status()
            print(f"✅ Notified {project['name']} successfully")
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"HTTP request failed: {e}")

    def _trigger_auto_update(self, project, payload):
        """Triggers an auto-update in a project via GitHub Actions."""
        if not project.get("owner") or not project.get("repo"):
            raise ValueError("Project owner/repo required for auto-update")

        workflow_payload = {
            "ref": "main",
            "inputs": {
                "force_update": "true",
                "triggered_by": "template_webhook",
                "template_version": payload["template"]["latest_version"],
            },
        }
        print(f"🔄 Triggering auto-update for {project['name']}...")
        print(f"Would trigger workflow in {project['owner']}/{project['repo']} with: {workflow_payload}")
        # In a real implementation, this would use the GitHub API.

    def _create_webhook_signature(self, payload_bytes):
        """Creates a webhook signature for security."""
        mac = hmac.new(self.webhook_secret.encode('utf-8'), msg=payload_bytes, digestmod=hashlib.sha256)
        return f"sha256={mac.hexdigest()}"

    def verify_webhook_signature(self, payload_bytes, signature):
        """Verifies a webhook signature."""
        expected_signature = self._create_webhook_signature(payload_bytes)
        return hmac.compare_digest(signature, expected_signature)

    def _load_project_registry(self):
        """Loads the project registry from a file."""
        if self.registry_path.exists():
            try:
                return json.loads(self.registry_path.read_text())
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load project registry: {e}")
        return []

    def _save_project_registry(self):
        """Saves the project registry to a file."""
        try:
            self.registry_path.write_text(json.dumps(self.deployed_projects, indent=2))
        except IOError as e:
            print(f"Error: Failed to save project registry: {e}")

    def register_project(self, config):
        """Registers a new project deployment."""
        print(f"📝 Registering project: {config['name']}")
        project_id = self.add_project(config)
        welcome_payload = {
            "event": "project_registered",
            "timestamp": datetime.utcnow().isoformat(),
            "project": {"id": project_id, "name": config["name"]},
            "message": "Your project has been registered for template update notifications",
            "actions": {
                "check_command": "/update-from-template --check",
                "unregister_info": f"Contact admin to unregister project ID: {project_id}",
            },
        }
        if config.get("webhook_url"):
            self._send_webhook({**config, "id": project_id}, welcome_payload)
        return project_id

    def list_projects(self):
        """Lists all registered projects."""
        return [
            {
                "id": p.get("id"),
                "name": p.get("name"),
                "deployed_version": p.get("deployed_version"),
                "last_notified": p.get("last_notified"),
                "auto_update": p.get("auto_update"),
                "critical_updates_only": p.get("critical_updates_only"),
            }
            for p in self.deployed_projects
        ]
