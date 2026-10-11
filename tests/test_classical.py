import unittest

from policy_lab.classical import (
    ScenarioValidationError,
    assignment_to_bitstring,
    bitstring_to_assignment,
    enumerate_violations,
    evaluate_assignment,
    explain_violation,
    validate_scenario,
)
from policy_lab.fixtures import get_scenario


def violation_bitstrings(scenario_id):
    scenario = get_scenario(scenario_id)
    result = enumerate_violations(scenario)
    return [
        assignment_to_bitstring(scenario, assignment)
        for assignment in result["violating_assignments"]
    ]


class ClassicalEvaluatorTests(unittest.TestCase):
    def test_original_policy_has_one_contracting_project_owner_violation(self):
        scenario = get_scenario("contractor_access")

        result = enumerate_violations(scenario)

        self.assertEqual(
            result,
            {
                "scenario_id": "contractor_access",
                "attribute_order": ["C", "R", "D", "M"],
                "total_assignments": 16,
                "violation_count": 1,
                "violating_assignments": [
                    {"C": True, "R": True, "D": True, "M": True}
                ],
            },
        )

    def test_corrected_policy_has_no_violations(self):
        result = enumerate_violations(get_scenario("contractor_access_corrected"))

        self.assertEqual(result["total_assignments"], 16)
        self.assertEqual(result["violation_count"], 0)
        self.assertEqual(result["violating_assignments"], [])

    def test_asymmetric_fixture_bitstring(self):
        self.assertEqual(violation_bitstrings("asymmetric"), ["1101"])

    def test_multiple_solution_fixture_bitstrings(self):
        self.assertEqual(violation_bitstrings("multiple_solution"), ["1101", "1111"])

    def test_overlapping_or_uses_or_not_xor(self):
        bitstrings = violation_bitstrings("overlapping_or")

        self.assertEqual(len(bitstrings), 6)
        self.assertIn("1101", bitstrings)
        self.assertIn("1111", bitstrings)

    def test_evaluate_assignment_returns_separate_policy_and_requirement_results(self):
        scenario = get_scenario("contractor_access")
        assignment = {"C": True, "R": True, "D": True, "M": True}

        result = evaluate_assignment(scenario, assignment)

        self.assertEqual(result, {"allowed": True, "forbidden": True, "violation": True})

    def test_bitstring_round_trip_uses_canonical_attribute_order(self):
        scenario = get_scenario("asymmetric")
        assignment = bitstring_to_assignment(scenario, "1101")

        self.assertEqual(assignment, {"C": True, "R": True, "D": False, "M": True})
        self.assertEqual(assignment_to_bitstring(scenario, assignment), "1101")

    def test_explain_violation_mentions_policy_and_requirement(self):
        scenario = get_scenario("contractor_access")
        message = explain_violation(
            scenario,
            {"C": True, "R": True, "D": True, "M": True},
        )

        self.assertIn("1111 is a violation", message)
        self.assertIn("implemented policy allows access", message)
        self.assertIn("security requirement forbids it", message)

    def test_validate_scenario_rejects_invalid_contract_inputs(self):
        bad_scenarios = [
            {},
            {
                "schema_version": "2.0",
                "id": "bad",
                "attributes": ["C"],
                "allow_any": [["C"]],
                "forbid_any": [["C"]],
            },
            {
                "schema_version": "1.0",
                "id": "bad",
                "attributes": ["C", "C"],
                "allow_any": [["C"]],
                "forbid_any": [["C"]],
            },
            {
                "schema_version": "1.0",
                "id": "bad",
                "attributes": ["C"],
                "allow_any": [["X"]],
                "forbid_any": [["C"]],
            },
            {
                "schema_version": "1.0",
                "id": "bad",
                "attributes": ["C"],
                "allow_any": [["C", "not:C"]],
                "forbid_any": [["C"]],
            },
            {
                "schema_version": "1.0",
                "id": "bad",
                "attributes": ["C"],
                "allow_any": [["C"], ["C"]],
                "forbid_any": [["C"]],
            },
        ]

        for bad_scenario in bad_scenarios:
            with self.subTest(bad_scenario=bad_scenario):
                with self.assertRaises(ScenarioValidationError):
                    validate_scenario(bad_scenario)

    def test_assignment_must_match_declared_attributes_exactly(self):
        scenario = get_scenario("contractor_access")

        with self.assertRaises(ValueError):
            evaluate_assignment(scenario, {"C": True, "R": True, "D": True})


if __name__ == "__main__":
    unittest.main()
