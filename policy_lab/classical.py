"""Exact classical policy evaluation for CipherQ Policy Lab."""

from __future__ import annotations

from itertools import product
from typing import Any


Scenario = dict[str, Any]
Assignment = dict[str, bool]


class ScenarioValidationError(ValueError):
    """Raised when a scenario does not match the shared interface."""


def validate_scenario(scenario: Scenario) -> Scenario:
    """Validate a scenario against the v1 shared interface."""

    if not isinstance(scenario, dict):
        raise ScenarioValidationError("Scenario must be a dictionary.")

    required_fields = {"schema_version", "id", "attributes", "allow_any", "forbid_any"}
    actual_fields = set(scenario)
    missing = required_fields - actual_fields
    unknown = actual_fields - required_fields
    if missing:
        raise ScenarioValidationError(f"Scenario is missing fields: {sorted(missing)}.")
    if unknown:
        raise ScenarioValidationError(f"Scenario has unknown fields: {sorted(unknown)}.")

    if scenario["schema_version"] != "1.0":
        raise ScenarioValidationError('schema_version must be "1.0".')

    if not isinstance(scenario["id"], str) or not scenario["id"]:
        raise ScenarioValidationError("id must be a nonempty string.")

    attributes = scenario["attributes"]
    if not isinstance(attributes, list):
        raise ScenarioValidationError("attributes must be a list.")
    if not 1 <= len(attributes) <= 4:
        raise ScenarioValidationError("attributes must contain one to four names.")
    if len(set(attributes)) != len(attributes):
        raise ScenarioValidationError("attributes must be unique.")
    for attribute in attributes:
        if (
            not isinstance(attribute, str)
            or len(attribute) != 1
            or not attribute.isascii()
            or not attribute.isupper()
            or not attribute.isalpha()
        ):
            raise ScenarioValidationError(
                "attribute names must be single uppercase ASCII letters."
            )

    declared = set(attributes)
    _validate_rule("allow_any", scenario["allow_any"], declared)
    _validate_rule("forbid_any", scenario["forbid_any"], declared)
    return scenario


def evaluate_assignment(scenario: Scenario, assignment: Assignment) -> dict[str, bool]:
    """Evaluate permission, forbidden condition and violation for one assignment."""

    validate_scenario(scenario)
    _validate_assignment(scenario, assignment)

    allowed = _evaluate_rule(scenario["allow_any"], assignment)
    forbidden = _evaluate_rule(scenario["forbid_any"], assignment)
    return {
        "allowed": allowed,
        "forbidden": forbidden,
        "violation": allowed and forbidden,
    }


def enumerate_violations(scenario: Scenario) -> dict[str, Any]:
    """Exhaustively enumerate all assignments and return exact violations."""

    validate_scenario(scenario)
    attributes = scenario["attributes"]
    violating_assignments: list[Assignment] = []

    for values in product([False, True], repeat=len(attributes)):
        assignment = dict(zip(attributes, values, strict=True))
        if evaluate_assignment(scenario, assignment)["violation"]:
            violating_assignments.append(assignment)

    return {
        "scenario_id": scenario["id"],
        "attribute_order": list(attributes),
        "total_assignments": 2 ** len(attributes),
        "violation_count": len(violating_assignments),
        "violating_assignments": violating_assignments,
    }


def assignment_to_bitstring(scenario: Scenario, assignment: Assignment) -> str:
    """Render an assignment in canonical attribute order with false=0 and true=1."""

    validate_scenario(scenario)
    _validate_assignment(scenario, assignment)
    return "".join("1" if assignment[attribute] else "0" for attribute in scenario["attributes"])


def bitstring_to_assignment(scenario: Scenario, bitstring: str) -> Assignment:
    """Parse a canonical display bitstring into an assignment."""

    validate_scenario(scenario)
    attributes = scenario["attributes"]
    if not isinstance(bitstring, str) or len(bitstring) != len(attributes):
        raise ValueError("bitstring length must match the attribute order.")
    if any(bit not in {"0", "1"} for bit in bitstring):
        raise ValueError('bitstring may contain only "0" and "1".')
    return {
        attribute: bit == "1"
        for attribute, bit in zip(attributes, bitstring, strict=True)
    }


def explain_violation(scenario: Scenario, assignment: Assignment) -> str:
    """Produce a short human-readable explanation for a violating assignment."""

    result = evaluate_assignment(scenario, assignment)
    bitstring = assignment_to_bitstring(scenario, assignment)
    if not result["violation"]:
        return f"{bitstring} is not a violation because access and prohibition are not both true."

    true_attributes = [
        attribute for attribute in scenario["attributes"] if assignment[attribute]
    ]
    return (
        f"{bitstring} is a violation: the implemented policy allows access and "
        f"the security requirement forbids it. True attributes: "
        f"{', '.join(true_attributes) if true_attributes else 'none'}."
    )


def _validate_rule(name: str, rule: Any, declared: set[str]) -> None:
    if not isinstance(rule, list):
        raise ScenarioValidationError(f"{name} must be a list of conjunctions.")
    if not 1 <= len(rule) <= 2:
        raise ScenarioValidationError(f"{name} must contain one or two conjunctions.")

    seen_conjunctions: set[tuple[str, ...]] = set()
    for conjunction in rule:
        if not isinstance(conjunction, list) or not conjunction:
            raise ScenarioValidationError(f"{name} conjunctions must be nonempty lists.")

        positive: set[str] = set()
        negative: set[str] = set()
        normalized_literals: list[str] = []
        for literal in conjunction:
            attribute, is_negated = _parse_literal(literal)
            if attribute not in declared:
                raise ScenarioValidationError(f"literal references unknown attribute {attribute}.")
            if is_negated:
                negative.add(attribute)
            else:
                positive.add(attribute)
            normalized_literals.append(literal)

        if len(set(normalized_literals)) != len(normalized_literals):
            raise ScenarioValidationError("a conjunction cannot contain duplicate literals.")
        if positive & negative:
            raise ScenarioValidationError(
                "a conjunction cannot contain both an attribute and its negation."
            )

        key = tuple(sorted(normalized_literals))
        if key in seen_conjunctions:
            raise ScenarioValidationError("duplicate conjunctions are not supported.")
        seen_conjunctions.add(key)


def _validate_assignment(scenario: Scenario, assignment: Assignment) -> None:
    if not isinstance(assignment, dict):
        raise ValueError("assignment must be a dictionary.")
    expected = set(scenario["attributes"])
    actual = set(assignment)
    if actual != expected:
        raise ValueError("assignment must contain exactly the declared attributes.")
    if any(type(value) is not bool for value in assignment.values()):
        raise ValueError("assignment values must be booleans.")


def _evaluate_rule(rule: list[list[str]], assignment: Assignment) -> bool:
    return any(
        all(_evaluate_literal(literal, assignment) for literal in conjunction)
        for conjunction in rule
    )


def _evaluate_literal(literal: str, assignment: Assignment) -> bool:
    attribute, is_negated = _parse_literal(literal)
    value = assignment[attribute]
    return not value if is_negated else value


def _parse_literal(literal: Any) -> tuple[str, bool]:
    if not isinstance(literal, str) or not literal:
        raise ScenarioValidationError("literals must be nonempty strings.")
    if literal.startswith("not:"):
        attribute = literal.removeprefix("not:")
        if not attribute:
            raise ScenarioValidationError("negated literals must name an attribute.")
        return attribute, True
    return literal, False
