"""Qollab compatibility probe, not the policy oracle or application.

Place this file and probe_helper.py at the Qollab project's root.
Qollab supplies backend and invokes main through its Run dialog.
"""

import json
import sys
import time
from importlib.metadata import PackageNotFoundError, version

import qiskit
from qiskit import QuantumCircuit
from qiskit.providers.jobstatus import JobStatus

from probe_helper import IMPORT_MARKER, canonical_counts


def main(shots: int = 128, superposition: bool = False):
    if type(shots) is not int or not 1 <= shots <= 4096:
        raise ValueError("shots must be an integer between 1 and 4096")
    if type(superposition) is not bool:
        raise ValueError("superposition must be a Boolean")

    packages = {}
    for package in ("qiskit", "numpy", "qiskit-ionq"):
        try:
            packages[package] = version(package)
        except PackageNotFoundError:
            packages[package] = "distribution metadata unavailable"
    print(json.dumps({
        "python": sys.version,
        "qiskit_module_version": getattr(qiskit, "__version__", "unavailable"),
        "packages": packages,
        "companion_import": IMPORT_MARKER,
    }))

    # Synthetic wiring fixture: q0=1, q1=0. Not a policy violation.
    circuit = QuantumCircuit(2, 2)
    circuit.x(0)
    if superposition:
        circuit.h(1)
    circuit.measure([0, 1], [0, 1])
    selected_backend = globals().get("backend")
    if selected_backend is None:
        raise RuntimeError("Run in Qollab with its injected backend")
    backend_name = getattr(selected_backend, "name", None)
    if callable(backend_name):
        backend_name = backend_name()
    print(json.dumps({
        "backend": str(backend_name) if backend_name is not None else "unavailable",
        "total_qubits": circuit.num_qubits,
        "shots_requested": shots,
        "superposition": superposition,
    }))
    # Exactly one circuit submitted in exactly one job per invocation.
    job = selected_backend.run(circuit, shots=shots)
    deadline = time.monotonic() + 300
    while True:
        status = job.status()
        if status == JobStatus.DONE:
            break
        if status in (JobStatus.ERROR, JobStatus.CANCELLED):
            raise RuntimeError(f"Execution failed: {status}")
        if time.monotonic() >= deadline:
            raise TimeoutError("Stopped waiting after 300s; remote job may still run")
        time.sleep(1)
    counts = dict(job.result().get_counts())
    decoded = canonical_counts(counts)
    observed = sum(decoded.values())
    if observed != shots:
        raise RuntimeError(f"Expected {shots} shots, received {observed}")
    print(json.dumps({
        "result_kind": "current_execution",
        "raw_counts": counts,
        "canonical_order": ["q0", "q1"],
        "canonical_counts": decoded,
        "shots_observed": observed,
        "ideal_expected_support": ["10", "11"] if superposition else ["10"],
        "ideal_support_only": set(decoded) <= ({"10", "11"} if superposition else {"10"}),
    }))
