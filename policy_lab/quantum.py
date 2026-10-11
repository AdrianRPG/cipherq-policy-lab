"""Quantum circuit building blocks for Policy Lab."""

from qiskit import QuantumCircuit
from policy_lab.classical import validate_scenario

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

def apply_rule(
    circuit: QuantumCircuit,
    conjunctions: list[list[str]],
    attribute_qubits: dict[str, int],
    target: int,
    clause_qubits: list[int],
) -> None:
    """Toggle target when any conjunction is satisfied.

    Assumes the rule has passed scenario validation.

    Provide one clean auxiliary qubit per conjunction.
    Auxiliary qubits must start at zero and are restored to zero.
    All workspace qubits must be separate from the attributes.
    """
    if not conjunctions:
        raise ValueError("A rule must contain at least one conjunction.")

    if len(clause_qubits) != len(conjunctions):
        raise ValueError("Provide one auxiliary qubit per conjunction.")

    workspace = [target] + clause_qubits

    if len(set(workspace)) != len(workspace):
        raise ValueError("Workspace qubits must be distinct.")

    if set(workspace) & set(attribute_qubits.values()):
        raise ValueError("Workspace cannot overlap attribute qubits.")

    # Store each conjunction's truth value in its own auxiliary.
    for literals, clause_qubit in zip(conjunctions, clause_qubits):
        apply_conjunction(
            circuit, literals, attribute_qubits, clause_qubit
        )

    # OR is true unless every conjunction is false.
    circuit.x(target)

    for clause_qubit in clause_qubits:
        circuit.x(clause_qubit)

    if len(clause_qubits) == 1:
        circuit.cx(clause_qubits[0], target)
    else:
        circuit.mcx(clause_qubits, target)

    for clause_qubit in reversed(clause_qubits):
        circuit.x(clause_qubit)

    # Erase temporary conjunction values.
    for literals, clause_qubit in reversed(
        list(zip(conjunctions, clause_qubits))
    ):
        apply_conjunction(
            circuit, literals, attribute_qubits, clause_qubit
        )

def build_phase_oracle(scenario: dict) -> QuantumCircuit:
    """Compile policy rules into a violation-marking phase oracle.

    Attribute qubits follow scenario["attributes"] order.
    All remaining qubits are auxiliaries and must start at zero.

    The oracle preserves attribute values, changes the phase of
    violating assignments, and restores all auxiliaries to zero.
    """
    validate_scenario(scenario)

    attributes = scenario["attributes"]
    attribute_qubits = {
        name: index for index, name in enumerate(attributes)
    }

    n = len(attributes)
    permission_qubit = n
    forbidden_qubit = n + 1

    # Each rule cleans its temporary clause qubits, so both rules
    # can reuse the same workspace.
    workspace_size = max(
        len(scenario["allow_any"]),
        len(scenario["forbid_any"]),
    )
    workspace = list(range(n + 2, n + 2 + workspace_size))

    circuit = QuantumCircuit(
        n + 2 + workspace_size,
        name="policy_oracle",
    )

    permission_workspace = workspace[:len(scenario["allow_any"])]
    forbidden_workspace = workspace[:len(scenario["forbid_any"])]

    # Compute whether access is allowed.
    apply_rule(
        circuit,
        scenario["allow_any"],
        attribute_qubits,
        permission_qubit,
        permission_workspace,
    )

    # Compute whether the assignment is forbidden.
    apply_rule(
        circuit,
        scenario["forbid_any"],
        attribute_qubits,
        forbidden_qubit,
        forbidden_workspace,
    )

    # Introduce a minus sign only when both conditions are true.
    circuit.cz(permission_qubit, forbidden_qubit)

    # Uncompute the forbidden condition.
    apply_rule(
        circuit,
        scenario["forbid_any"],
        attribute_qubits,
        forbidden_qubit,
        forbidden_workspace,
    )

    # Uncompute permission.
    apply_rule(
        circuit,
        scenario["allow_any"],
        attribute_qubits,
        permission_qubit,
        permission_workspace,
    )

    return circuit

def apply_diffuser(
    circuit: QuantumCircuit,
    search_qubits: list[int],
) -> None:
    """Apply Grover diffusion to the attribute register only.

    Implements inversion about the mean up to a global phase,
    which does not affect measurement probabilities.
    Auxiliary qubits are not included.
    """
    if not search_qubits:
        raise ValueError("The search register cannot be empty.")

    if len(set(search_qubits)) != len(search_qubits):
        raise ValueError("Search qubits must be distinct.")

    for qubit in search_qubits:
        circuit.h(qubit)
        circuit.x(qubit)

    # Apply a phase flip when every search qubit is 1.
    if len(search_qubits) == 1:
        circuit.z(search_qubits[0])
    else:
        target = search_qubits[-1]
        controls = search_qubits[:-1]

        circuit.h(target)
        circuit.mcx(controls, target)
        circuit.h(target)

    for qubit in search_qubits:
        circuit.x(qubit)
        circuit.h(qubit)

def build_search_circuit(scenario: dict, iterations: int) -> dict:
    """Build a measured Grover search circuit and its metadata.

    Uses the policy rules directly, without classical solutions.
    Zero iterations produces the uniform-sampling baseline.
    """
    validate_scenario(scenario)

    if type(iterations) is not int or not 0 <= iterations <= 4:
        raise ValueError(
            "iterations must be an integer from 0 through 4."
        )

    attributes = list(scenario["attributes"])
    n = len(attributes)

    attribute_qubits = {
        name: index for index, name in enumerate(attributes)
    }
    attribute_clbits = dict(attribute_qubits)
    search_qubits = list(range(n))

    oracle = build_phase_oracle(scenario)

    # Classical bits are allocated only for attribute measurements.
    circuit = QuantumCircuit(
        oracle.num_qubits,
        n,
        name="policy_search",
    )

    # Prepare a uniform superposition of attribute assignments.
    # Auxiliary qubits remain at zero.
    circuit.h(search_qubits)

    # Each Grover iteration applies the oracle, then diffusion.
    for _ in range(iterations):
        circuit.compose(oracle, inplace=True)
        apply_diffuser(circuit, search_qubits)

    # Measure attributes only; do not measure auxiliary qubits.
    for attribute in attributes:
        circuit.measure(
            attribute_qubits[attribute],
            attribute_clbits[attribute],
        )

    return {
        "scenario_id": scenario["id"],
        "circuit": circuit,
        "attribute_order": attributes,
        "attribute_qubits": attribute_qubits,
        "attribute_clbits": attribute_clbits,
        "iterations": iterations,
        "total_qubits": circuit.num_qubits,
    }