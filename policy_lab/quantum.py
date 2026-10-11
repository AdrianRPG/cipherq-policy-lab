"""Quantum circuit building blocks for Policy Lab."""

from qiskit import QuantumCircuit


def apply_conjunction(
    circuit: QuantumCircuit,
    literals: list[str],
    attribute_qubits: dict[str, int],
    target: int,
) -> None:
    """Toggle target when every literal is satisfied.

    Assumes literals have passed scenario validation.
    The target must be separate from the attribute qubits.

    When target starts at zero, it stores the conjunction's value.
    Applying this operation again uncomputes that value.
    """
    if not literals:
        raise ValueError("A conjunction must contain at least one literal.")

    controls = []
    negative_controls = []

    for literal in literals:
        is_negative = literal.startswith("not:")
        attribute = literal[4:] if is_negative else literal
        qubit = attribute_qubits[attribute]

        controls.append(qubit)
        if is_negative:
            negative_controls.append(qubit)

    if target in controls:
        raise ValueError("The target cannot also be a control qubit.")

    # Convert negative conditions into controls on the value 1.
    for qubit in negative_controls:
        circuit.x(qubit)

    # Toggle the target only when all controls are 1.
    if len(controls) == 1:
        circuit.cx(controls[0], target)
    else:
        circuit.mcx(controls, target)

    # Restore the original attribute values.
    for qubit in reversed(negative_controls):
        circuit.x(qubit)