# Policy Lab — Project Context

## Status

Policy Lab is a new project by team CipherQ for the Qollab × IonQ Global Quantum Hackathon.

The team has created and cloned its GitHub repository and established collaborator access. Application implementation and Qollab compatibility have not yet been verified.

Plans in this document are not claims of completed functionality.

## Purpose

Build an educational tool that translates small access-control policies into quantum search problems.

Users should understand how a policy violation becomes a Boolean predicate, how that predicate becomes a quantum oracle, and how Grover's algorithm changes the probability of observing a violating assignment.

Primary theme: Quantum Unlocked.

## Minimum working experience

A user can:

1. Select a small, clearly labeled synthetic security scenario.
2. Inspect its implemented access policy and separate security requirement.
3. Run a Grover circuit compiled from the rules.
4. Inspect measured assignments and explanations of actual violations.
5. Compare the quantum results with an exact classical reference.
6. Examine a corrected policy and understand the change.

Initial scope: four Boolean attributes, followed by a second meaningful scenario and constrained rule editing once the first complete path works.

## Initial security scenario

Attributes:

- C: the person is a contractor.
- R: the person is responsible for the project.
- D: the person uses a managed device.
- M: the person completed multifactor authentication.

All 16 combinations are valid inputs in this illustrative model. A contractor may also be responsible for a project.

Implemented permission:
R AND D AND M

Forbidden condition:
C

Violation:
Implemented permission AND forbidden condition

Exactly one assignment violates the initial requirement:
C=true, R=true, D=true, M=true.

Corrected permission:
NOT C AND R AND D AND M

The corrected policy has zero violating assignments.

This known example is a correctness fixture. The implementation must compile supported rules, not hardcode this answer.

## Team ownership

- Adrian: quantum oracle, Grover circuit, security interpretation, captain coordination and final submission.
- Boris: Qollab compatibility, execution integration, user-facing inputs and outputs, dependencies and publication packaging.
- Piero: classical policy evaluation, exact reference results, independent validation, experimental analysis and charts.

Ownership is flexible. Coordinate overlapping edits and shared-interface changes.

Every teammate must understand the complete demonstration.

## Architecture

One scenario feeds two independent paths:

- Classical evaluation: enumerate assignments and establish exact reference results.
- Quantum evaluation: compile the rules into an oracle, construct Grover's circuit, execute and decode measurements.

Reporting compares the results and explains counterexamples.

The quantum builder must not consume the classical list of solutions to construct its oracle.

The authoritative technical contract will live in docs/INTERFACE.md. Keep exact schemas there rather than duplicating them here.

## Scientific boundaries

- A measured candidate is a violation only after checking its attributes against the predicate.
- Failure to sample a violation does not prove that none exists.
- Exact no-violation claims in the small model come from exhaustive classical verification.
- A simulator experiment does not establish practical quantum speedup.
- If a benchmark uses the known number of solutions to choose Grover iterations, disclose that information.
- Oracle tests must check phase behavior and restoration of auxiliary qubits.
- Synthetic scenarios are educational examples, not evidence of vulnerabilities in a real university system.
- Attribute ordering and measurement decoding must be explicit and tested.

## Hackathon requirements

Based on the rules and organizer announcements supplied by the captain:

- Build the submitted contribution within the official hackathon window.
- Use Qiskit.
- Publish a public, runnable Qollab project under the MIT license.
- Verify execution on Qollab's built-in simulator and its IonQ simulator option.
- Provide a project page explaining purpose, method, execution, results and limitations.
- Follow UI accessibility best practices.
- Include a public 2–3 minute demonstration video.
- Attribute reused libraries, templates, code and explanations.
- Include: "This effort is supported by Qollab & IonQ".
- Keep the published project available for the required 12 months.
- The captain submits through the team page.
- Submission deadline: October 11, 2026, at 7:00 p.m. Eastern Time.

GitHub is the development repository. It does not replace Qollab publication or the submission action.

## Platform constraints reported by organizers

- Built-in simulator: Qiskit BasicSimulator in the browser, maximum 24 qubits.
- IonQ options: reported maximums of 25 or 29 qubits depending on the selected model.
- Within Qollab, an IonQ execution permits one job containing one circuit.
- Multiple experiments must respect that per-execution restriction.
- No automatic persistence between project runs.
- External dependencies of the submitted experience must satisfy the organizers' public-access, licensing and API-key requirements.

Count all qubits, including auxiliaries. Avoid designing close to the maximum.

These are organizer-reported constraints, not completed compatibility tests.

## Decisions still requiring verification

Boris will establish and document:

- Available Python, Qiskit and package versions.
- Supported project files and imports.
- Supported input controls and output presentation.
- The actual procedure for running on each required backend.
- How project publication and updates work.

Do not assume that React, Streamlit, a separate server or an arbitrary package is supported.

## Scope control

Prioritize one working end-to-end experiment, then expand.

Initially exclude:

- Natural-language policy interpretation.
- Production identity-management integrations.
- Authentication systems and databases.
- Paid APIs or GPU training.
- Claims of outperforming production security tools.

Use new, labeled synthetic scenarios. Prior projects are background experience, not this hackathon's submitted work.

## Keeping context current

Record consequential team decisions here and technical contract changes in docs/INTERFACE.md.

Distinguish planned, implemented and verified behavior.

When a newer organizer announcement changes a requirement, record the update and its source before relying on it.