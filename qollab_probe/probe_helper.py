"""Companion-file import and explicit measurement decoding probe."""

IMPORT_MARKER = "policy-lab-companion-import-ok"


def canonical_counts(raw_counts):
    """Display q0 then q1; Qiskit prints the single register as c1 c0."""
    decoded = {}
    for bits, count in raw_counts.items():
        if not isinstance(bits, str) or len(bits) != 2 or set(bits) - {"0", "1"}:
            raise ValueError(f"Unexpected two-bit measurement key: {bits!r}")
        if type(count) is not int or count < 0:
            raise ValueError(f"Unexpected measurement count: {count!r}")
        decoded[bits[::-1]] = count
    return decoded
