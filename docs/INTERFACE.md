# Policy Lab — Shared Interface v1

Status: initial contract for team review before implementation.

## 1. Scenario format

A scenario is a JSON object:

{
  "schema_version": "1.0",
  "id": "contractor_access",
  "attributes": ["C", "R", "D", "M"],
  "allow_any": [["R", "D", "M"]],
  "forbid_any": [["C"]]
}

Attribute meanings for this example:

- C: contractor.
- R: responsible for the project.
- D: managed device.
- M: multifactor authentication completed.

All combinations are valid in this initial model.

## 2. Rule interpretation

- Each inner list is a conjunction: AND.
- The outer list joins conjunctions using OR.
- A literal such as "C" requires C=true.
- A literal such as "not:C" requires C=false.
- Permission is the evaluation of allow_any.
- Forbidden is the evaluation of forbid_any.
- Violation = permission AND forbidden.

Example:

[["R", "D"], ["M"]]

means:

(R AND D) OR M

The quantum implementation must implement OR correctly, including overlapping true terms. XOR is not a substitute for OR.

## 3. Initial validation limits

For the first implementation:

- Support one to four unique attributes.
- Attribute names are single uppercase ASCII letters.
- id is a nonempty string.
- schema_version must be "1.0".
- Each rule contains one or two nonempty conjunctions.
- Literals reference declared attributes only.
- A conjunction cannot contain duplicate literals or both an attribute and its negation.
- Duplicate conjunctions are rejected.
- Missing fields, unknown fields and invalid types are rejected.
- Unsupported input produces a clear validation error.

These are application limits, not simulator capacity claims.

Any expansion of these limits requires checking circuit resources and coordinating the change.

## 4. Assignments and ordering

An assignment is a dictionary containing exactly the declared attributes with Boolean values.

Example:

{"C": true, "R": true, "D": true, "M": true}

The attributes array defines canonical display order.

For ["C", "R", "D", "M"], display string "1001" means:

C=true, R=false, D=false, M=true.

Canonical display strings are not raw Qiskit measurement strings.

The runner must decode measurements using the circuit's explicit qubit and classical-bit mapping.

## 5. Classical component

evaluate_assignment(scenario, assignment)

Returns:

{
  "allowed": true,
  "forbidden": true,
  "violation": true
}

enumerate_violations(scenario)

Returns:

{
  "scenario_id": "contractor_access",
  "attribute_order": ["C", "R", "D", "M"],
  "total_assignments": 16,
  "violation_count": 1,
  "violating_assignments": [
    {"C": true, "R": true, "D": true, "M": true}
  ]
}

Return assignments in lexicographic canonical bit-string order, with 0 before 1.

Owner: Piero.

## 6. Quantum component

build_search_circuit(scenario, iterations)

Inputs:

- A valid scenario.
- An integer iteration count from 0 through 4.
- No classical solution list.

Returns a Python dictionary containing:

- circuit: a Qiskit QuantumCircuit.
- attribute_order: ordered attribute names.
- attribute_qubits: mapping from each attribute to its circuit qubit index.
- attribute_clbits: mapping from each attribute to its measurement bit index.
- iterations: the requested iteration count.
- total_qubits: all circuit qubits, including auxiliaries.

Measure only the attribute register in the submitted search circuit, using one classical register with matching width.

Restore auxiliary qubits before the diffuser. Apply diffusion to the search register.

Iteration count 0 provides the uniform-sampling reference circuit.

The implementation may expose additional internal helpers for testing the oracle.

Owner: Adrian.

## 7. Execution component

run_search(search_spec, backend, shots)

Inputs:

- search_spec: the quantum builder's output.
- backend: the execution backend supplied by the integration layer.
- shots: a positive integer, default 512.

Responsibilities:

- Execute one circuit in one backend job.
- Decode raw results into canonical attribute order.
- Return integer measurement counts.
- Report execution failure explicitly rather than substituting sample data.

Returns:

{
  "scenario_id": "contractor_access",
  "attribute_order": ["C", "R", "D", "M"],
  "iterations": 3,
  "shots_requested": 512,
  "shots_observed": 512,
  "backend": "actual backend identifier",
  "counts": {
    "1111": 480,
    "0000": 32
  }
}

The counts above are illustrative, not measured results.

Include scenario_id in search_spec as metadata so the runner can return it.

All count keys use canonical display order. Counts must sum to shots_observed.

Record the actual backend and noise-model selection, when applicable. Do not invent metadata unavailable from the platform.

Adapt backend-specific APIs inside this layer while preserving the shared output.

Owner: Boris.

## 8. Reporting

The report receives:

- The scenario.
- Classical reference results.
- Decoded execution results.

For every sampled assignment, evaluate the violation predicate.

Observed violation proportion:

sum of counts for violating assignments / shots_observed

Uniform reference probability:

violation_count / total_assignments

Do not calculate the observed proportion if shots_observed is zero; report an error.

For zero violations, state:

"Exhaustive classical verification found no violations within this model."

Do not attribute that proof to quantum sampling.

Saved results and current execution results must be visibly distinguished.

Boris owns presentation; Piero owns comparative analysis; Adrian reviews quantum explanations.

## 9. Required fixtures

Original policy:

allow_any = [["R", "D", "M"]]
forbid_any = [["C"]]

Expected violation: "1111".

Corrected policy:

allow_any = [["not:C", "R", "D", "M"]]
forbid_any = [["C"]]

Expected violations: none.

Asymmetric fixture:

allow_any = [["R", "not:D", "M"]]
forbid_any = [["C"]]

Expected violation: "1101".

Multiple-solution fixture:

allow_any = [["R", "M"]]
forbid_any = [["C"]]

Expected violations: "1101" and "1111".

Overlapping-OR fixture:

allow_any = [["R"], ["M"]]
forbid_any = [["C"]]

Expected violation count: 6.
Assignments satisfying both R and M must remain allowed.

All fixtures use attribute order ["C", "R", "D", "M"] and are synthetic.

## 10. Contract changes

Coordinate changes with affected teammates before implementation.

Update this document and the relevant tests together.

Keep the quantum compiler independent of the classical answer list. Share input validation and data definitions where appropriate, but retain independent checks of quantum behavior.