# Qollab compatibility — Boris

Status: asymmetric probe verified on both the built-in simulator and IonQ Aria 1 simulator in the private [Qollab draft](https://qollab.xyz/u/bmino/cipherq-policy-lab-2). The later full application checks are recorded in [INTEGRATION.md](INTEGRATION.md). This page retains historical probe evidence.

Local checks completed: both Python files parse successfully; decoder checks passed for asymmetric and multiple outcomes and rejected malformed keys, negative counts, noninteger counts and Boolean counts. Local Python is 3.10.11 with no Qiskit installed, so no local circuit execution was performed. These checks do not establish Qollab compatibility.

## Documentation inspected

- [Create a Project](https://qollab.xyz/learn/building-your-first-qollab-project/create-project): Python projects use root-level `main.py`; supported annotated `main()` parameters become run settings. The starter uses the supplied `backend`. Creation confirms linked terms; a draft is private until publication.
- [Code Playground](https://qollab.xyz/learn/building-your-first-qollab-project/code-playground): backend selection occurs in Select QPU; built-in and remote IonQ simulators are available and documented as free. Console output can be copied or downloaded. The guide lists Chrome, Edge, Opera and Firefox 153+; Safari is unsupported.

These are documentation findings; execution evidence is tracked separately below. The initial editor inspection required sign-in; authenticated access subsequently succeeded.

## Observed built-in execution

The draft's starter requirements are `qiskit>=2.5.2,<3.0.0`. They were retained. The probe ran with Python 3.14.2, Qiskit 2.5.2 and NumPy 2.4.6. Qiskit-IonQ distribution metadata was unavailable on the built-in run. The companion file imported successfully, and Qollab generated Shots and Superposition controls from `main()`.

With 128 shots and Superposition false, `basic_simulator` returned raw `01: 128`, decoded to canonical `10: 128`, as expected. The UI reported 1.5 seconds; this is not a quantum performance benchmark. See [saved console transcription](experiments/qollab-built-in-probe.json). Console download/copy was attempted but did not yield an artifact through browser automation; the JSON is explicitly a transcription.

## Observed IonQ execution

Selected **IonQ Aria 1 (25q), Noise model, Free**, under Remotely Run Simulators. The run reported backend `ionq_simulator`, Python 3.14.2, Qiskit 2.5.2, NumPy 2.4.6 and Qiskit-IonQ 1.0.2. Companion import succeeded. With 128 shots and Superposition false, raw counts were `01: 128`, decoded to `10: 128`. The UI reported 13.9 seconds and displayed the two-qubit circuit and probabilities. See [saved console transcription](experiments/qollab-ionq-aria1-probe.json). No physical hardware was used. The selected noise-model label is recorded from the UI; the probe does not independently inspect the service's noise configuration.

## Probe procedure

1. Open a private Python / Qiskit draft in a supported browser. Copy `qollab_probe/main.py` and `qollab_probe/probe_helper.py` into its root as `main.py` and `probe_helper.py`. Retain the platform starter requirements for this probe; record their exact contents. No dependency version is pinned until tested.
2. Choose Run Project → Run. Check that Shots and Superposition controls appear. Use 128 shots and Superposition false.
3. Select the built-in ideal simulator. Save the full console output. Expected raw counts: `01: 128`; expected canonical counts in q0,q1 order: `10: 128`. Two qubits total, zero auxiliaries. This asymmetric fixture detects reversed bit ordering.
4. Run separately with Superposition true. Ideal support is raw `01`/`11`, canonical `10`/`11`; the exact split is random, with equal theoretical probabilities.
5. In a separate execution choose an IonQ **simulator**, record the exact selected model, and repeat. Each invocation submits only one circuit in one job. No hardware run is needed. Noise can produce other outcomes; retain all counts and report the deviation rather than filtering it away.
6. Repeat after reopening the project to check reproducibility without relying on run persistence. Save output locally as evidence; label it as a saved experiment.

The probe prints Python/package versions, companion-import confirmation, supplied backend name, raw and decoded counts and shot totals. It does not print credentials or environment variables. Missing distribution metadata is reported explicitly and does not establish that a module is absent. A timeout stops waiting without cancelling the remote job; inspect its state before retrying.

## Superposition and reload checks

The checkbox was changed to true and the probe executed separately on each backend, still one circuit and one job per run:

| Backend | Raw counts | Canonical q0,q1 counts | Shots |
| --- | --- | --- | --- |
| Built-in | `01: 68, 11: 60` | `10: 68, 11: 60` | 128 |
| IonQ Aria 1 | `01: 55, 11: 73` | `10: 55, 11: 73` | 128 |

The split is stochastic; the ideal theoretical probability is 1/2 for each supported outcome. The observed samples are not exact probability estimates or policy violations. Transcriptions are in `docs/experiments/qollab-*-superposition.json` and screenshots are alongside them.

Before the built-in superposition run, the project page was reloaded. The saved files loaded and companion import succeeded again; the console and backend choice reset. This verifies page-reload reproduction in the same authenticated browser, not reproduction on another device or independent account. No code change was needed for either backend.

## Verification status

| Check | Status |
| --- | --- |
| Python/Qiskit/package versions inside Qollab | Verified for both backends; see above |
| Companion Python file import | Passed on both backends |
| Annotated integer/Boolean controls | Defaults executed correctly; Boolean toggle changed circuit and output |
| Console JSON output and saved output | JSON displayed; transcription saved; download unverified |
| Built-in ideal execution and asymmetric decoding | Passed: 128/128 canonical `10` |
| Selected IonQ simulator/model and returned counts | Passed: Aria 1, 128/128 canonical `10` |
| Page-reload reproduction | Passed on built-in; separate device/account still unverified |

At the probe checkpoint, the private draft contained the probe as `main.py`, `probe_helper.py`, the unchanged starter requirements, and the existing Project Card. The application integration subsequently replaced the draft entry point; the original probe remains in `qollab_probe/`. It has not been published. To repeat, open Code → Run Project → Run, set Shots to 128, choose Superposition, then select either tested simulator. The later integration uses `docs/INTERFACE.md`; see `INTEGRATION.md` for its separate verification evidence.

This probe establishes integration wiring only. It does not validate the policy compiler, oracle phase, auxiliary cleanup or the complete application. The shared component contract remains in `docs/INTERFACE.md`.
