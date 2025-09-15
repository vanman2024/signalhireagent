import json
from typing import Any


def load_contacts_from_file(file_path: str) -> list[dict[str, Any]]:
    with open(file_path) as f:
        data = json.load(f)
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and 'contacts' in data:
            return data['contacts']
        raise ValueError(f"Unrecognized JSON schema in {file_path}")

def filter_contacts_by_job_title(contacts: list[dict[str, Any]], exclude_titles: list[str]) -> list[dict[str, Any]]:
    exclude_lower = [title.lower() for title in exclude_titles]
    filtered = []
    for c in contacts:
        job_title = c.get('job_title', '').lower()
        if not any(excl in job_title for excl in exclude_lower):
            filtered.append(c)
    return filtered

def save_contacts_to_file(contacts: list[dict[str, Any]], output_path: str):
    with open(output_path, 'w') as f:
        json.dump(contacts, f, indent=2)
