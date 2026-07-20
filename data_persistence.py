"""
Data Persistence Module

Baseline (in code) + custom additions, stored durably in the shared GCS state
bucket on Cloud Run (local files in dev), via empirica_core.storage.JsonStore.
Writes are gated: only admin/management sessions persist changes — everyone else
is read-only (avoids concurrent-edit conflicts). Same public API as before, so
pages don't change.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from baseline_data import (
    get_baseline_team,
    get_baseline_opex,
    get_baseline_wholesale,
)
from empirica_core.storage import JsonStore, session_can_write

# Keys (object names) in the durable store.
TEAM = "custom_team_members.json"
OPEX = "custom_opex_expenses.json"
WHOLESALE = "custom_wholesale_deals.json"
ASSUMPTIONS = "model_assumptions.json"
QBO = "qbo_actuals.json"
FUNDRAISING = "fundraising_rounds.json"
PO = "po_data.json"


class DataStore:
    """Persistent storage for Alma dashboard data (durable + write-gated)."""

    def __init__(self, data_dir: str = "data"):
        local = Path(__file__).parent / data_dir
        self._store = JsonStore(
            app_key="alma",
            bucket="empirica-portals-state" if os.environ.get("K_SERVICE") else None,
            local_dir=local,
        )

    # --- internals ---------------------------------------------------------
    def _save(self, key: str, payload_field: str, value) -> None:
        """Persist ``{payload_field: value, last_updated}`` — writers only."""
        if not session_can_write():
            return
        self._store.write(key, {payload_field: value,
                                "last_updated": datetime.now().isoformat()})

    def _load(self, key: str, payload_field: str, default):
        data = self._store.read(key)
        return data.get(payload_field, default) if data else default

    @staticmethod
    def _dedupe(items, key_fn, baseline):
        """Return only ``items`` whose key isn't already in ``baseline``."""
        baseline_ids = {key_fn(b) for b in baseline}
        return [it for it in items if key_fn(it) not in baseline_ids]

    # --- Team --------------------------------------------------------------
    def save_team_members(self, all_team_members: List[Dict[str, Any]]):
        custom = self._dedupe(
            all_team_members,
            lambda m: f"{m['first_name']}_{m['last_name']}_{m.get('start_date', '')}",
            get_baseline_team(),
        )
        self._save(TEAM, "custom_team_members", custom)

    def load_team_members(self) -> List[Dict[str, Any]]:
        return get_baseline_team() + self._load(TEAM, "custom_team_members", [])

    # --- OpEx --------------------------------------------------------------
    def save_opex_expenses(self, all_expenses: List[Dict[str, Any]]):
        custom = self._dedupe(
            all_expenses,
            lambda e: f"{e['expense_name']}_{e.get('start_date', '')}",
            get_baseline_opex(),
        )
        self._save(OPEX, "custom_expenses", custom)

    def load_opex_expenses(self) -> List[Dict[str, Any]]:
        return get_baseline_opex() + self._load(OPEX, "custom_expenses", [])

    # --- Wholesale ---------------------------------------------------------
    def save_wholesale_deals(self, all_deals: List[Dict[str, Any]]):
        custom = self._dedupe(
            all_deals,
            lambda d: f"{d['customer_name']}_{d.get('close_date', '')}",
            get_baseline_wholesale(),
        )
        self._save(WHOLESALE, "custom_deals", custom)

    def load_wholesale_deals(self) -> List[Dict[str, Any]]:
        return get_baseline_wholesale() + self._load(WHOLESALE, "custom_deals", [])

    # --- Assumptions -------------------------------------------------------
    def save_assumptions(self, assumptions: Dict[str, Any]):
        self._save(ASSUMPTIONS, "assumptions", assumptions)

    def load_assumptions(self) -> Dict[str, Any]:
        return self._load(ASSUMPTIONS, "assumptions", {})

    # --- QBO actuals -------------------------------------------------------
    def save_qbo_actuals(self, qbo_data: Dict[str, Any]):
        self._save(QBO, "qbo_actuals", qbo_data)

    def load_qbo_actuals(self) -> Dict[str, Any]:
        return self._load(QBO, "qbo_actuals", {})

    # --- Fundraising -------------------------------------------------------
    def save_fundraising(self, rounds: List[Dict[str, Any]]):
        self._save(FUNDRAISING, "fundraising_rounds", rounds)

    def load_fundraising(self) -> List[Dict[str, Any]]:
        return self._load(FUNDRAISING, "fundraising_rounds", [])

    # --- Purchase orders ---------------------------------------------------
    def save_po_data(self, po_list: List[Dict[str, Any]]):
        self._save(PO, "po_data", po_list)

    def load_po_data(self) -> List[Dict[str, Any]]:
        return self._load(PO, "po_data", [])

    # --- Utility -----------------------------------------------------------
    def clear_all_data(self):
        if not session_can_write():
            return
        for key in (TEAM, OPEX, WHOLESALE, ASSUMPTIONS, QBO, FUNDRAISING, PO):
            self._store.delete(key)

    def get_last_updated(self, data_type: str) -> str:
        key = {"team": TEAM, "opex": OPEX, "wholesale": WHOLESALE,
               "assumptions": ASSUMPTIONS}.get(data_type)
        if not key:
            return "Never"
        data = self._store.read(key)
        return data.get("last_updated", "Unknown") if data else "Never"


# Global instance
_store = None


def get_data_store() -> DataStore:
    global _store
    if _store is None:
        _store = DataStore()
    return _store
