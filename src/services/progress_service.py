import json
from typing import Any


class ProgressTracker:
    def __init__(self, progress_file: str):
        self.progress_file = progress_file
        self.progress = self.load_progress()

    def load_progress(self) -> dict[str, Any]:
        try:
            with open(self.progress_file) as f:
                return json.load(f)
        except FileNotFoundError:
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
