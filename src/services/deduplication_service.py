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
            else:
                raise ValueError(f"Unrecognized JSON schema in {path}")
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
