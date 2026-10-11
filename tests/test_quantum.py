"""Correctness tests for Policy Lab's quantum building blocks."""

import unittest

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from policy_lab.quantum import apply_conjunction


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


if __name__ == "__main__":
    unittest.main()