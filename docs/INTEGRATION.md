# Integrated policy experiment

Boris's integration branch connects Adrian's compiler and Piero's evaluator from merged commit `7f31db2`, without changing their implementations or the shared interface. Entry point: `main.py`; execution: `policy_lab/execution.py`; reporting: `policy_lab/application.py`.

## Run in Qollab

The private [draft](https://qollab.xyz/u/bmino/cipherq-policy-lab-2) contains root `main.py` and the `policy_lab/` package. To update another draft, archive those paths at the archive root and use Browse → Files → Unpack → Keep and add. This preserves other project files while replacing matching paths. Retain the starter requirements; no new third-party dependency is needed beyond Qiskit and its dependencies. The old `probe_helper.py` is harmless and unused by the application.

Choose Code → Run Project → Run. Set Scenario Choice, Iterations (0–4), and Shots (1–4096). Pick the built-in ideal simulator or the free IonQ Aria 1 simulator under Remotely Run Simulators. Each invocation submits exactly one circuit in one job. The runner lowers multi-controlled gates to rx/ry/rz/cx plus measurement without adding qubits or changing the classical-bit mapping.

| Scenario Choice | Synthetic fixture | Exact violating assignments in C,R,D,M order |
| --- | --- | --- |
| 0 | Original contractor access | `1111` |
| 1 | Corrected policy | None |
| 2 | Asymmetric / negative device literal | `1101` |
| 3 | Multiple solutions | `1101`, `1111` |
| 4 | Overlapping OR | Six assignments; evaluate through the classical reference |

Use three iterations for the initial one-of-16 teaching fixture and zero for a uniform baseline. Three is a disclosed setting based on that known fixture, not automatic tuning and not a general optimum. The compiler receives rules and iterations only, never the reference solution list. The original and corrected circuits use seven total qubits, including three auxiliaries; overlapping OR uses eight.

## Read results

Console candidate strings use C,R,D,M order. Each candidate lists attribute values and a separate classical verdict. Qollab's automatic probability panel uses its own raw qubit-order display, which can include leading auxiliary bits; use our console/report for canonical assignments. All counts are retained, including nonviolations.

The exact uniform reference is the classically enumerated violation count divided by 16. Measured frequencies fluctuate. Zero-violation proof comes exclusively from exhaustive classical verification in this small model, never sampling. Circuit size and simulator wall time do not establish practical quantum advantage.

The program writes `policy_lab_result.json` with `saved_experiment` labeling and also prints a complete JSON report. File creation succeeded in Qollab; file download UI has not yet been verified. Repository evidence under `docs/experiments/integration-*.json` is copied from the rendered console JSON and explicitly marked as saved experiments.

## Verification

- Local: 23 unittest tests passed on Python 3.10.11, Qiskit 2.5.2 and NumPy 2.2.6. Includes classical truth tables, oracle phases, clean auxiliaries, Grover amplitudes, all five scenario integration paths, a zero-iteration baseline, permuted classical-bit mapping, malformed counts and execution failures. No engine source was modified.
- Qollab built-in original: 512 shots, 3 iterations, 487 verified violations (95.12%), exact uniform reference 6.25%; seven qubits.
- Qollab built-in corrected: 512 shots, 3 iterations, zero verified violations; exhaustive classical reference zero.
- Qollab IonQ Aria 1 noise-model original: 512 shots, 3 iterations, 116 verified violations (22.66%), compared with the exact uniform reference 6.25%. Corrected: 512 shots, 3 iterations, zero verified violations; exhaustive classical reference zero.
- Qollab asymmetric fixture: built-in 496/512 verified `1101` violations (96.88%); IonQ Aria 1 130/512 (25.39%). Three iterations, seven qubits. The built-in application run succeeded after a page reload, reimporting the saved package in the same authenticated browser.
- All six saved Qollab reports were rechecked locally: count totals, reference enumeration, every candidate verdict, and reported violation proportions matched.
- Local CLI `python main.py --scenario 2 --iterations 3 --shots 128` completed and wrote its saved-result JSON. This local output is ignored by Git and is not presented as Qollab evidence.

The original circuit was transpiled to 537 operations, depth 403; the corrected circuit to 967 operations, depth 794 (including measurements). The lower observed IonQ success fraction is consistent with its selected noise model, but this experiment does not isolate each source of error. Do not present the ideal and noisy samples as equivalent results.

Qollab runtime: Python 3.14.2, Qiskit 2.5.2, NumPy 2.4.6. IonQ application runs reported Qiskit-IonQ 1.0.2. Earlier two-qubit compatibility checks are historical probe evidence in `QOLLAB_COMPATIBILITY.md`.

The draft Project Card now contains the guide preserved in `docs/QOLLAB_PROJECT.md`, including scenario selection, bit ordering and scientific limitations. The private draft remains unpublished. The multiple-solution and overlapping-OR application paths passed locally; they have not yet been run on Qollab.

Still pending: independent teammate review, public publication, final educational presentation, required video and submission. A separate device/account reproduction has not been tested. Integration work lives on `feat/qollab-integration`; teammates must fetch that branch to review it. Other teammates' checkouts do not update automatically.
