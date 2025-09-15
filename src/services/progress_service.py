import json
from typing import Any


class ProgressTracker:
    def __init__(self, progress_file: str):
        self.progress_file = progress_file
        self.progress = self.load_progress()

    def load_progress(self) -> dict[str, Any]:
        try:
            with open(self.progress_file) as f:
                content = f.read().strip()
                if not content:
                    return {"revealed": [], "remaining": []}
                return json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"revealed": [], "remaining": []}

    def save_progress(self):
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)

    def mark_revealed(self, uid: str):
        if uid not in self.progress["revealed"]:
            self.progress["revealed"].append(uid)
            if uid in self.progress["remaining"]:
                self.progress["remaining"].remove(uid)
            self.save_progress()

    def get_remaining(self, all_uids: list[str]) -> list[str]:
        revealed = set(self.progress["revealed"])
        return [uid for uid in all_uids if uid not in revealed]

    def set_remaining(self, uids: list[str]):
        self.progress["remaining"] = uids
        self.save_progress()

    def check_reveal_quota(self, daily_limit: int = 5000) -> dict[str, Any]:
        """Check if reveal quota allows processing more contacts (FR-012)."""
        revealed_today = len(self.progress.get("revealed", []))
        remaining_quota = max(0, daily_limit - revealed_today)

        return {
            "revealed_today": revealed_today,
            "daily_limit": daily_limit,
            "remaining_quota": remaining_quota,
            "quota_exceeded": revealed_today >= daily_limit,
            "can_process_more": remaining_quota > 0
        }

    def add_reveal_result(self, uid: str, result_type: str, error: str = None):
        """Track reveal results with success/failure/linkedin-only distinction (FR-013)."""
        if "reveal_results" not in self.progress:
            self.progress["reveal_results"] = []

        result = {
            "uid": uid,
            "result_type": result_type,  # "success", "failed", "linkedin_only", "quota_exceeded"
            "timestamp": str(__import__('datetime').datetime.now()),
            "error": error
        }

        self.progress["reveal_results"].append(result)
        self.save_progress()

    def get_reveal_statistics(self) -> dict[str, Any]:
        """Get comprehensive reveal statistics."""
        results = self.progress.get("reveal_results", [])

        stats = {
            "total_attempts": len(results),
            "successful": len([r for r in results if r["result_type"] == "success"]),
            "failed": len([r for r in results if r["result_type"] == "failed"]),
            "linkedin_only": len([r for r in results if r["result_type"] == "linkedin_only"]),
            "quota_exceeded": len([r for r in results if r["result_type"] == "quota_exceeded"])
        }

        if stats["total_attempts"] > 0:
            stats["success_rate"] = stats["successful"] / stats["total_attempts"] * 100
        else:
            stats["success_rate"] = 0

        return stats
