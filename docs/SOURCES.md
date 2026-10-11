# Sources and AI assistance

## Qollab compatibility probe

- Qollab, [Create a Project](https://qollab.xyz/learn/building-your-first-qollab-project/create-project) and [Code Playground](https://qollab.xyz/learn/building-your-first-qollab-project/code-playground), accessed during the October 10–11, 2026 work session. Used to identify project entry points, backend injection, annotated run inputs, simulator selection and output behavior. Actual runtime verification is recorded separately in `docs/QOLLAB_COMPATIBILITY.md` and `docs/INTEGRATION.md`.
- OpenAI Codex assisted Boris with documentation inspection, authoring the compatibility probe and verification notes. The probe follows the documented `backend.run` / job status / result workflow. Its asymmetric synthetic fixture and decoding checks were authored for this project; they are not policy-search results.
- Codex subsequently entered the probe into Boris's private Qollab draft and executed four simulator checks: asymmetric and superposition fixtures on the built-in and IonQ Aria 1 simulators. Saved evidence in `docs/experiments/` is labeled as console transcription or screenshots. No physical hardware or publication was involved.

## Application integration

- Adrian's quantum compiler and Piero's classical evaluator are preserved from repository commit `7f31db2` (merged teammate PRs #2 and #3). Codex assisted Boris with the execution adapter, candidate reporting, Qollab entry point, tests, packaging and verification.
- [Qiskit-IonQ submission documentation](https://qiskit-community.github.io/qiskit-ionq/guides/usage.html), consulted for supported QIS gates. Integration lowers circuits to `rx`, `ry`, `rz`, `cx` plus measurements; actual Qollab verification is recorded separately from this documentation.
- The integrated application was run on the original, corrected and asymmetric fixtures on both Qollab's built-in simulator and its IonQ Aria 1 noise-model simulator. Codex saved rendered console reports, rechecked all six with the classical evaluator, and added draft project instructions. Twenty-three local tests passed. Details and limitations are in `docs/INTEGRATION.md`; the Qollab draft has not been published.
