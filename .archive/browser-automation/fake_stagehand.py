from __future__ import annotations

from typing import Any, Dict, List

from signalhire_agent.models.search_criteria import SearchCriteria
from signalhire_agent.models.prospect import Prospect
from signalhire_agent.models.contact_info import ContactInfo


class FakeStagehand:
    """A lightweight fake for Stagehand browser automation.

    Records calls for assertions and returns deterministic data structures.
    """

    def __init__(self) -> None:
        self.calls: List[Dict[str, Any]] = []

    async def login(self, email: str, password: str) -> bool:
        self.calls.append({"op": "login", "email": email})
        return True

    async def search(self, criteria: SearchCriteria) -> List[Prospect]:
        self.calls.append({"op": "search", "criteria": criteria.model_dump()})
        # Return a couple of deterministic prospects for tests
        return [
            Prospect(name="Ada Lovelace", title=criteria.title, company=criteria.company),
            Prospect(name="Grace Hopper", title=criteria.title, company=criteria.company),
        ]

    async def reveal(self, name: str) -> ContactInfo:
        self.calls.append({"op": "reveal", "name": name})
        return ContactInfo(email=f"{name.split()[0].lower()}@example.com")

    async def export_csv(self, prospects: List[Prospect]) -> str:
        self.calls.append({"op": "export", "n": len(prospects)})
        header = "name,title,company\n"
        rows = [f"{p.name},{p.title or ''},{p.company or ''}" for p in prospects]
        return header + "\n".join(rows)

