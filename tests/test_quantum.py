"""Correctness tests for Policy Lab's quantum building blocks."""

import unittest

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from policy_lab.quantum import (
    apply_conjunction,
    apply_rule,
    build_phase_oracle,
    apply_diffuser,
    build_search_circuit,
)
from policy_lab.classical import evaluate_assignment
from policy_lab.fixtures import get_scenario

ATTRIBUTE_QUBITS = {"C": 0, "R": 1, "D": 2, "M": 3}
TARGET = 4

CASES = [
    ["R", "D", "M"],
    ["not:C", "R"],
    ["not:C", "not:R"],
    ["C"],
    ["not:M"],
]


class TestConjunction(unittest.TestCase):
    def test_all_assignments(self):
        """Compare each circuit with its classical truth table."""
        for literals in CASES:
            for assignment in range(16):
                with self.subTest(
                    literals=literals, assignment=assignment
                ):
                    circuit = QuantumCircuit(5)

                    values = {
                        name: bool((assignment >> qubit) & 1)
                        for name, qubit in ATTRIBUTE_QUBITS.items()
                    }

                    for name, qubit in ATTRIBUTE_QUBITS.items():
                        if values[name]:
                            circuit.x(qubit)

                    satisfied = all(
                        not values[literal[4:]]
                        if literal.startswith("not:")
                        else values[literal]
                        for literal in literals
                    )

                    apply_conjunction(
                        circuit, literals, ATTRIBUTE_QUBITS, TARGET
                    )

                    expected = np.zeros(32, dtype=complex)
                    expected_index = assignment | (
                        int(satisfied) << TARGET
                    )
                    expected[expected_index] = 1.0

                    actual = Statevector.from_instruction(circuit)

                    np.testing.assert_allclose(
                        actual.data, expected, atol=1e-9, rtol=0
                    )

    def test_uncomputation_in_superposition(self):
        """Applying the operation twice restores the full state."""
        for literals in CASES:
            with self.subTest(literals=literals):
                circuit = QuantumCircuit(5)
                circuit.h([0, 1, 2, 3])
                initial = Statevector.from_instruction(circuit)

                apply_conjunction(
                    circuit, literals, ATTRIBUTE_QUBITS, TARGET
                )
                apply_conjunction(
                    circuit, literals, ATTRIBUTE_QUBITS, TARGET
                )

                restored = Statevector.from_instruction(circuit)

                np.testing.assert_allclose(
                    restored.data, initial.data, atol=1e-9, rtol=0
                )

RULE_CASES = [
    [["R", "D", "M"]],
    [["R"], ["M"]],
    [["not:C", "R"], ["M"]],
    [["C"], ["not:C"]],
]


class TestRule(unittest.TestCase):
    def test_rule_truth_tables_and_clean_auxiliaries(self):
        for rule in RULE_CASES:
            total_qubits = 5 + len(rule)
            clause_qubits = list(range(5, total_qubits))

            for assignment in range(16):
                with self.subTest(rule=rule, assignment=assignment):
                    circuit = QuantumCircuit(total_qubits)

                    values = {
                        name: bool((assignment >> qubit) & 1)
                        for name, qubit in ATTRIBUTE_QUBITS.items()
                    }

                    for name, qubit in ATTRIBUTE_QUBITS.items():
                        if values[name]:
                            circuit.x(qubit)

                    satisfied = any(
                        all(
                            not values[literal[4:]]
                            if literal.startswith("not:")
                            else values[literal]
                            for literal in clause
                        )
                        for clause in rule
                    )

                    apply_rule(
                        circuit, rule, ATTRIBUTE_QUBITS,
                        TARGET, clause_qubits
                    )

                    expected = np.zeros(2**total_qubits, dtype=complex)
                    expected[assignment | (int(satisfied) << TARGET)] = 1

                    actual = Statevector.from_instruction(circuit)

                    np.testing.assert_allclose(
                        actual.data, expected, atol=1e-9, rtol=0
                    )

    def test_rule_uncomputation_in_superposition(self):
        for rule in RULE_CASES:
            with self.subTest(rule=rule):
                total_qubits = 5 + len(rule)
                clause_qubits = list(range(5, total_qubits))

                circuit = QuantumCircuit(total_qubits)
                circuit.h([0, 1, 2, 3])
                initial = Statevector.from_instruction(circuit)

                for _ in range(2):
                    apply_rule(
                        circuit, rule, ATTRIBUTE_QUBITS,
                        TARGET, clause_qubits
                    )

                restored = Statevector.from_instruction(circuit)

                np.testing.assert_allclose(
                    restored.data, initial.data, atol=1e-9, rtol=0
                )

class TestPhaseOracle(unittest.TestCase):
    def test_phase_marking_and_auxiliary_cleanup(self):
        scenario_ids = [
            "contractor_access",
            "contractor_access_corrected",
            "asymmetric",
            "multiple_solution",
            "overlapping_or",
        ]

        for scenario_id in scenario_ids:
            with self.subTest(scenario=scenario_id):
                scenario = get_scenario(scenario_id)
                attributes = scenario["attributes"]
                n = len(attributes)

                oracle = build_phase_oracle(scenario)

                # Put all attribute assignments in superposition.
                # Auxiliary qubits start at zero.
                circuit = QuantumCircuit(oracle.num_qubits)
                circuit.h(list(range(n)))
                circuit.compose(oracle, inplace=True)

                actual = Statevector.from_instruction(circuit)

                # Build an independent reference for the test.
                expected = np.zeros(
                    2**oracle.num_qubits, dtype=complex
                )
                amplitude = 1 / np.sqrt(2**n)

                for basis_index in range(2**n):
                    assignment = {
                        name: bool((basis_index >> index) & 1)
                        for index, name in enumerate(attributes)
                    }

                    violation = evaluate_assignment(
                        scenario, assignment
                    )["violation"]

                    expected[basis_index] = (
                        -amplitude if violation else amplitude
                    )

                # Check phase marking and clean auxiliary qubits.
                self.assertTrue(
                    actual.equiv(Statevector(expected)),
                    msg=f"Incorrect oracle state: {scenario_id}",
                )

class TestDiffuser(unittest.TestCase):
    def test_inversion_about_mean_preserves_auxiliary(self):
        rng = np.random.default_rng(42)

        for n in range(1, 5):
            with self.subTest(attribute_qubits=n):
                size = 2**n

                # Prepare a reproducible state with complex amplitudes.
                search_state = (
                    rng.normal(size=size)
                    + 1j * rng.normal(size=size)
                )
                search_state /= np.linalg.norm(search_state)

                # Give the auxiliary its own nontrivial state.
                auxiliary_state = np.array(
                    [1, 1j], dtype=complex
                ) / np.sqrt(2)

                # Qiskit places higher-index qubits on the left
                # in the statevector tensor ordering.
                initial = np.kron(auxiliary_state, search_state)

                circuit = QuantumCircuit(n + 1)
                apply_diffuser(circuit, list(range(n)))

                actual = Statevector(initial).evolve(circuit)

                # Independent mathematical definition of diffusion.
                reflected = (
                    2 * np.mean(search_state) - search_state
                )
                expected = np.kron(auxiliary_state, reflected)

                self.assertTrue(
                    actual.equiv(Statevector(expected)),
                    msg=f"Diffuser failed for {n} attribute qubits",
                )

class TestSearchCircuit(unittest.TestCase):
    def test_grover_amplitudes_and_clean_auxiliaries(self):
        scenario_ids = [
            "contractor_access",
            "contractor_access_corrected",
            "asymmetric",
            "multiple_solution",
            "overlapping_or",
        ]

        for scenario_id in scenario_ids:
            scenario = get_scenario(scenario_id)
            attributes = scenario["attributes"]
            n = len(attributes)
            size = 2**n

            # Classical reference used only by this test.
            violating_indices = set()

            for index in range(size):
                assignment = {
                    name: bool((index >> position) & 1)
                    for position, name in enumerate(attributes)
                }
                if evaluate_assignment(scenario, assignment)["violation"]:
                    violating_indices.add(index)

            solution_count = len(violating_indices)

            for iterations in range(5):
                with self.subTest(
                    scenario=scenario_id, iterations=iterations
                ):
                    spec = build_search_circuit(scenario, iterations)

                    # Inspect the state immediately before measurement.
                    circuit = spec["circuit"].remove_final_measurements(
                        inplace=False
                    )
                    actual = Statevector.from_instruction(circuit)

                    expected = np.zeros(
                        2**circuit.num_qubits, dtype=complex
                    )

                    if solution_count == 0 or solution_count == size:
                        # The state remains uniform up to global phase.
                        expected[:size] = 1 / np.sqrt(size)
                    else:
                        theta = np.arcsin(
                            np.sqrt(solution_count / size)
                        )
                        angle = (2 * iterations + 1) * theta

                        marked_amplitude = (
                            np.sin(angle) / np.sqrt(solution_count)
                        )
                        unmarked_amplitude = (
                            np.cos(angle)
                            / np.sqrt(size - solution_count)
                        )

                        for index in range(size):
                            expected[index] = (
                                marked_amplitude
                                if index in violating_indices
                                else unmarked_amplitude
                            )

                    self.assertTrue(
                        actual.equiv(Statevector(expected)),
                        msg=(
                            f"Incorrect Grover state: "
                            f"{scenario_id}, iterations={iterations}"
                        ),
                    )

    def test_invalid_iterations_are_rejected(self):
        scenario = get_scenario("contractor_access")

        for invalid in [-1, 5, True, False, 1.5, "3", None]:
            with self.subTest(iterations=invalid):
                with self.assertRaises(ValueError):
                    build_search_circuit(scenario, invalid)


if __name__ == "__main__":
    unittest.main()