# Policy Lab — Implementation Workflows

Read `context.md` and `AGENTS.md` first. Use `docs/INTERFACE.md` as the authoritative technical contract once agreed.

These workflows describe planned work, not completed capabilities.

## Shared starting point

Before building components independently:

- Agree on the scenario format and component inputs/outputs.
- Fix the attribute order and document how it maps to circuit registers.
- Use the same initial scenario and corrected-policy fixture.
- Identify any unresolved contract details before implementing dependent code.

Owners can work concurrently once these agreements are in place.

## 1. Classical policy evaluation

Owner: Piero.

### Build

1. Validate scenarios according to the shared contract.
2. Evaluate the implemented permission and forbidden condition separately.
3. Identify a violation when both conditions are true.
4. Enumerate all assignments for the small supported attribute set.
5. Return the exact violating assignments and total number of assignments.

### Verify

- Initial scenario: exactly one violation.
- Corrected scenario: zero violations.
- A scenario with multiple violations.
- Negative literals and multiple alternative rules.
- Invalid inputs and unknown attributes.
- Asymmetric assignments that expose ordering mistakes.

### Hand off

Provide the evaluator, test fixtures, actual test results and an example output matching the shared contract.

The classical results are a reference for validation and reporting. They must not become the quantum oracle's list of targets.

## 2. Quantum oracle and Grover circuit

Owner: Adrian.

### Build

1. Read and validate the supported scenario representation.
2. Compile the permission and forbidden conditions into reversible logic.
3. Mark assignments satisfying their conjunction through a phase change.
4. Uncompute temporary calculations so auxiliary qubits return to their initial state.
5. Add state preparation and Grover iterations.
6. Measure the attribute register and provide explicit decoding metadata.

Start with the smallest supported case before expanding rule coverage.

### Verify

- The oracle marks precisely the expected assignments, up to an irrelevant global phase.
- Auxiliary qubits are restored.
- Phase tests use an appropriate reference or superposition; basis-state measurement probabilities alone are insufficient.
- Grover's diffuser acts on the intended search register.
- Negative literals, multiple solutions and no-solution cases behave correctly.
- Measurement decoding works for asymmetric assignments.

### Hand off

Provide the circuit builder, register mapping, chosen iteration count, circuit resource counts, tests and known limits.

Disclose any classical solution-count information used to select iterations in benchmarks. Do not describe that as an independent search advantage.

## 3. Qollab integration and presentation

Owner: Boris.

### Establish compatibility first

1. Inspect available Python/Qiskit versions and packages.
2. Check project file imports and supported inputs/outputs.
3. Run a small measured circuit on the built-in simulator.
4. Run a small measured circuit through Qollab's IonQ option.
5. Record verified behavior and any restrictions.

Select presentation tools only after checking platform support.

### Build

1. Provide a way to select or configure a supported scenario.
2. Connect the classical evaluator and quantum builder using the shared contract.
3. Execute one circuit in one job per IonQ run.
4. Decode results using the supplied register metadata.
5. Present policies, measured assignments, verified violations and classical reference results.
6. Handle invalid inputs, execution failures and zero-violation results clearly.

Use labeled controls, readable text and explanations that do not depend on color alone.

### Hand off

Provide the runnable entry point, tested dependency versions, execution instructions and evidence of compatibility.

Clearly label temporary sample outputs and replace them in the actual execution path before completion.

## 4. Integration checkpoint

Owners: all three.

Connect one scenario through the complete path:

Scenario → classical reference and quantum circuit → execution → decoded results → explanation.

Confirm that:

- All components use the same attribute meanings and ordering.
- Reported measurements come from the actual execution.
- Candidates are checked before being described as violations.
- The original and corrected scenarios produce understandable reports.
- A fresh session can reproduce the documented behavior.

Integrate this small example before adding features.

## 5. Experiments and educational explanation

Lead: Piero, with Adrian reviewing quantum claims and Boris integrating presentation.

Compare the original policy, corrected policy and at least one meaningfully different case.

Record:

- Scenario and parameters.
- Backend and whether the result is ideal or noise-model simulation.
- Shots and Grover iterations.
- Exact classical solution count.
- Observed proportion of violating assignments.
- Circuit qubits, including auxiliaries, and relevant gate/depth information.
- Package versions and reproducibility settings.
- Limitations and any failed or inconclusive experiment.

Explain the connection from security rule to predicate to oracle to measurement.

Distinguish theoretical expectations, recorded experiments and current runs. Include sampling uncertainty when interpreting measured proportions.

## 6. Publication and submission

Adrian coordinates and submits.
Boris verifies the published execution.
Piero independently checks reproduction and reported results.

1. Publish an early working version on Qollab.
2. Verify the required simulator paths.
3. Complete the project page and run instructions.
4. Include MIT licensing, source attribution and the required acknowledgment.
5. Explain the original contribution and scientific limitations.
6. Produce the public 2–3 minute demonstration video.
7. Check all submission links and access requirements.
8. Submit through the team page before the deadline in `context.md`.
9. Verify the submission confirmation.

GitHub publication alone is not the hackathon submission.

## Handoff format

For each completed task, report:

- Completed behavior.
- Changed files and branch or pull-request link.
- How another teammate runs or uses it.
- Checks actually performed.
- Remaining limitations and next owner.

Update shared contracts through team coordination. Do not silently change inputs or outputs.