import json
from typing import Any


def load_contacts_from_files(file_paths: list[str]) -> list[dict[str, Any]]:
    contacts = []
    for path in file_paths:
        with open(path) as f:
            data = json.load(f)
            if isinstance(data, list):
                contacts.extend(data)
            elif isinstance(data, dict) and 'contacts' in data:
                contacts.extend(data['contacts'])
            elif isinstance(data, dict):
                # Try to find contact-like data in any array field
                for key, value in data.items():
                    if isinstance(value, list) and value and isinstance(value[0], dict):
                        # Check if this looks like contact data (has name or uid or linkedin_url)
                        first_item = value[0]
                        if any(
                            field in first_item
                            for field in ['name', 'uid', 'linkedin_url', 'job_title']
                        ):
                            contacts.extend(value)
                            break
                else:
                    # No contact-like data found, log warning but continue
                    print(
                        f"Warning: No recognizable contact data found in {path}, skipping file"
                    )
            else:
                print(f"Warning: Unrecognized JSON format in {path}, skipping file")
    return contacts


def deduplicate_contacts(contacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen_uids = set()
    seen_linkedin = set()
    deduped = []
    for c in contacts:
        uid = c.get('uid')
        linkedin = c.get('linkedin_url')
        if uid and uid not in seen_uids:
            seen_uids.add(uid)
            deduped.append(c)
        elif not uid and linkedin and linkedin not in seen_linkedin:
            seen_linkedin.add(linkedin)
            deduped.append(c)
        # else: duplicate, skip
    return deduped


def save_contacts_to_file(contacts: list[dict[str, Any]], output_path: str):
    with open(output_path, 'w') as f:
        json.dump(contacts, f, indent=2)


def create_backup_files(file_paths: list[str]) -> list[str]:
    """Create backup copies of input files before processing."""
    import shutil
    from datetime import datetime

    backup_paths = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for file_path in file_paths:
        if not file_path or not file_path.strip():
            continue

        # Create backup filename
        path_parts = file_path.rsplit('.', 1)
        if len(path_parts) == 2:
            backup_path = f"{path_parts[0]}_backup_{timestamp}.{path_parts[1]}"
        else:
            backup_path = f"{file_path}_backup_{timestamp}"

        try:
            shutil.copy2(file_path, backup_path)
            backup_paths.append(backup_path)
            print(f"Created backup: {backup_path}")
        except Exception as e:
            print(f"Warning: Could not create backup for {file_path}: {e}")

    return backup_paths
