# CipherQ Policy Lab

Explore how a small access-control policy becomes a quantum search problem. These are synthetic educational scenarios, not real security findings.

## Try it

Open **Code → Run Project → Run**. Select the built-in simulator for ideal behavior or **IonQ Aria 1** under **Remotely Run Simulators** for a noise-model simulation.

Set **Scenario Choice**:

| Choice | Scenario |
| --- | --- |
| 0 | Original policy: contractors can receive forbidden access |
| 1 | Corrected policy: contractors explicitly excluded |
| 2 | Asymmetric example: access requires an unmanaged device |
| 3 | Multiple violating assignments |
| 4 | Overlapping alternative permission rules |

Use **Iterations = 3**, **Shots = 512** for the original example. Three iterations is chosen for the known one-of-16 teaching fixture; it is not optimal for every scenario. Set Iterations to **0** for uniform sampling. Each run submits one circuit in one job.

## Understand the result

The console uses **C, R, D, M** order: contractor, responsible for the project, managed device, multifactor authentication. `1101` means contractor=true, responsible=true, managed device=false, MFA=true. The automatic probability chart uses Qollab's raw bit order, so refer to the console for attribute assignments.

The original permission is R AND D AND M. The security requirement forbids C. A violation satisfies both permission and prohibition. The corrected permission adds NOT C.

Adrian's quantum compiler builds the oracle directly from rules. Piero's independent classical evaluator exhaustively checks all 16 assignments. Boris's execution and reporting layer decodes measurements and checks every measured candidate before calling it a violation.

The console labels current execution and prints complete JSON. Saved result files are labeled separately. A sample with no violations is not proof of absence; exact zero-violation conclusions come from exhaustive classical verification within this model. No practical quantum advantage is claimed.

## Team and attribution

CipherQ: Adrian Perez Galindo, Boris Steeven Mino, Piero Espinoza. MIT license. Built with Qiskit and Qollab; AI assistance and sources are recorded in the GitHub repository's `docs/SOURCES.md`.

This effort is supported by Qollab & IonQ
