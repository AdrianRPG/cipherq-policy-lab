"""One-circuit execution and explicit classical-bit decoding for Qollab."""
import time
from numbers import Integral

from qiskit import transpile
from qiskit.providers.jobstatus import JobStatus


def decode_counts(raw_counts, attribute_order, attribute_clbits):
    width = len(attribute_order)
    if set(attribute_clbits) != set(attribute_order):
        raise ValueError('Measurement mapping must cover every attribute.')
    positions = list(attribute_clbits.values())
    if any(type(p) is not int for p in positions) or set(positions) != set(range(width)):
        raise ValueError('Measurement mapping must be a permutation of the classical bits.')
    counts = {}
    for raw, count in raw_counts.items():
        if not isinstance(raw, str) or len(raw) != width or set(raw) - {'0', '1'}:
            raise ValueError(f'Expected one {width}-bit register, received {raw!r}.')
        if isinstance(count, bool) or not isinstance(count, Integral) or count < 0:
            raise ValueError('Backend counts must be nonnegative integers.')
        key = ''.join(raw[width - 1 - attribute_clbits[a]] for a in attribute_order)
        counts[key] = counts.get(key, 0) + int(count)
    return counts


def run_search(search_spec, backend, shots=512):
    if type(shots) is not int or shots <= 0:
        raise ValueError('shots must be a positive integer.')
    order = search_spec['attribute_order']
    mapping = search_spec['attribute_clbits']
    decode_counts({}, order, mapping)
    circuit = search_spec['circuit']
    if len(circuit.cregs) != 1 or circuit.num_clbits != len(order):
        raise ValueError('Expected one classical register measuring attributes only.')
    if circuit.num_qubits != search_spec['total_qubits']:
        raise ValueError('Circuit qubit count does not match metadata.')
    # Universal QIS gates accepted by both tested simulator paths. This lowers
    # multi-controlled operations without adding qubits or remapping measurements.
    executable = transpile(circuit, basis_gates=['rx', 'ry', 'rz', 'cx'], optimization_level=1)
    name = getattr(backend, 'name', None)
    name = name() if callable(name) else name
    if name is None:
        raise ValueError('Backend identifier is unavailable.')
    print(f'Executing one circuit: {executable.num_qubits} total qubits, '
          f'depth {executable.depth()}, {executable.size()} operations; backend={name}')
    job = backend.run(executable, shots=shots)
    deadline = time.monotonic() + 300
    previous_status = None
    while True:
        status = job.status()
        if status != previous_status:
            print(f'Job status: {status}')
            previous_status = status
        if status == JobStatus.DONE:
            break
        if status in (JobStatus.ERROR, JobStatus.CANCELLED):
            raise RuntimeError(f'Backend execution failed: {status}')
        if time.monotonic() >= deadline:
            raise TimeoutError('Stopped waiting after 300s; remote job may still run. Check before retrying.')
        time.sleep(1)
    counts = decode_counts(job.result().get_counts(), order, mapping)
    observed = sum(counts.values())
    if observed <= 0 or observed != shots:
        raise RuntimeError(f'Expected {shots} shots, received {observed}.')
    return {
        'scenario_id': search_spec['scenario_id'],
        'attribute_order': list(order),
        'iterations': search_spec['iterations'],
        'shots_requested': shots,
        'shots_observed': observed,
        'backend': str(name),
        'counts': counts,
    }
