# CipherQ Policy Lab

An educational quantum policy-auditing lab built with Qiskit.

Policy Lab explores how access-control rules become Boolean predicates and quantum oracles, how Grover's algorithm searches for violations, and how quantum measurements compare with exact classical verification.

Built for the Qollab × IonQ Global Quantum Hackathon 2026.

**Theme:** Quantum Unlocked  
**Team:** CipherQ — Florida International University

## Current status

Project setup and shared documentation are in progress.

Application functionality, dependency versions and Qollab/IonQ execution have not yet been verified. The features below describe the planned implementation.

## Planned experience

1. Select a small synthetic security scenario.
2. Inspect the implemented access policy and the separate security requirement.
3. Compile the violation predicate into a quantum oracle.
4. Execute Grover's algorithm and inspect measured assignments.
5. Explain verified counterexamples.
6. Compare results against exhaustive classical evaluation.
7. Examine a corrected policy.

The intended contribution goes beyond a fixed-target Grover demonstration: supported policy rules determine the oracle, and results connect measured assignments to understandable security violations.

## Initial example

A system grants access when a person:

- Is responsible for a project.
- Uses a managed device.
- Has completed multifactor authentication.

A separate security requirement prohibits contractors from accessing the protected documents.

Policy Lab investigates whether someone can satisfy the implemented permission while violating that requirement.

All scenarios are synthetic educational examples.

## How the components connect

Scenario
→ Classical evaluation and quantum circuit construction
→ Quantum execution
→ Measurement decoding
→ Counterexample validation and explanation

The classical evaluator supplies an exact reference. Its solution list is not used to construct the quantum oracle.

## Team

| Member | Primary responsibility |
| --- | --- |
| Adrian Perez Galindo | Quantum oracle, Grover circuit, security interpretation and captain duties |
| Boris Steeven Mino | Qollab integration, execution, presentation and publication packaging |
| Piero Espinoza | Classical evaluator, validation, experiments and analysis |

Responsibilities are flexible; coordinate shared changes before implementation.

## Repository documents

- [context.md](context.md): project scope, requirements and decisions.
- [AGENTS.md](AGENTS.md): team and AI-assistant working agreement.
- [workflows.md](workflows.md): implementation responsibilities and handoffs.
- [docs/INTERFACE.md](docs/INTERFACE.md): proposed shared technical contract.

Before implementation, the team must review and agree on the interface contract.

## Running the project

Verified installation and execution instructions will be added after the first working integration.

The submission must run on Qollab's built-in simulator and its IonQ simulator option. GitHub is the development repository, not a replacement for the Qollab submission.

## Classical evaluator

The first exact reference implementation lives in `policy_lab.classical`.
It validates v1 scenarios, evaluates implemented permission and forbidden
requirements separately, and exhaustively enumerates violating assignments.

Run the current classical checks with:

```bash
python3 -m unittest discover -s tests -v
```

Example usage:

```python
from policy_lab.classical import enumerate_violations
from policy_lab.fixtures import get_scenario

scenario = get_scenario("contractor_access")
reference = enumerate_violations(scenario)
```

## Scientific limitations

- Quantum sampling that finds no violation does not prove that no violation exists.
- Exact no-violation conclusions apply to the defined small model and come from exhaustive classical verification.
- Simulator results do not establish practical quantum speedup.
- Any use of known solution counts to choose Grover iterations must be disclosed.
- Policy Lab is an educational prototype, not a production security-auditing system.

## Contributing

Work on feature branches and use focused pull requests with one teammate review before merging.

Describe what changed, what was tested, and any remaining limitations. Keep shared contracts and documentation current.

## License and attribution

Project code and documentation are released under the [MIT License](LICENSE).

External sources and reused material will be recorded in `docs/SOURCES.md` as development proceeds.

This effort is supported by Qoll
