"""Shared synthetic scenarios for classical validation and integration tests."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


BASE_ATTRIBUTES = ["C", "R", "D", "M"]


SCENARIOS: dict[str, dict[str, Any]] = {
    "contractor_access": {
        "schema_version": "1.0",
        "id": "contractor_access",
        "attributes": BASE_ATTRIBUTES,
        "allow_any": [["R", "D", "M"]],
        "forbid_any": [["C"]],
    },
    "contractor_access_corrected": {
        "schema_version": "1.0",
        "id": "contractor_access_corrected",
        "attributes": BASE_ATTRIBUTES,
        "allow_any": [["not:C", "R", "D", "M"]],
        "forbid_any": [["C"]],
    },
    "asymmetric": {
        "schema_version": "1.0",
        "id": "asymmetric",
        "attributes": BASE_ATTRIBUTES,
        "allow_any": [["R", "not:D", "M"]],
        "forbid_any": [["C"]],
    },
    "multiple_solution": {
        "schema_version": "1.0",
        "id": "multiple_solution",
        "attributes": BASE_ATTRIBUTES,
        "allow_any": [["R", "M"]],
        "forbid_any": [["C"]],
    },
    "overlapping_or": {
        "schema_version": "1.0",
        "id": "overlapping_or",
        "attributes": BASE_ATTRIBUTES,
        "allow_any": [["R"], ["M"]],
        "forbid_any": [["C"]],
    },
}


def get_scenario(scenario_id: str) -> dict[str, Any]:
    """Return a mutable copy of a named synthetic scenario."""

    if scenario_id not in SCENARIOS:
        raise KeyError(f"Unknown scenario fixture: {scenario_id}")
    return deepcopy(SCENARIOS[scenario_id])
