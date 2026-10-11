"""Qollab entry point. Scenario: 0 original, 1 corrected, 2 asymmetric,
3 multiple solutions, 4 overlapping OR. Each run submits one circuit/job.
"""
import json
import sys
from importlib.metadata import PackageNotFoundError, version
from policy_lab.application import run_experiment


def main(scenario_choice: int = 0, iterations: int = 3, shots: int = 512):
    selected_backend = globals().get('backend')
    if selected_backend is None:
        raise RuntimeError('Qollab must supply backend; locally run: python main.py')
    report = run_experiment(selected_backend, scenario_choice, iterations, shots)
    report['runtime'] = {'python': sys.version}
    for package in ('qiskit', 'numpy', 'qiskit-ionq'):
        try:
            report['runtime'][package] = version(package)
        except PackageNotFoundError:
            report['runtime'][package] = 'distribution metadata unavailable'
    # Downloadable evidence is explicitly a saved experiment.
    saved = dict(report, result_kind='saved_experiment')
    with open('policy_lab_result.json', 'w') as handle:
        json.dump(saved, handle, indent=2)
    print('Saved this execution to policy_lab_result.json. Record the selected noise-model label separately.')
    print(json.dumps(report))
    return report


if __name__ == '__main__' and 'backend' not in globals():
    import argparse
    from qiskit.providers.basic_provider import BasicSimulator
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scenario', type=int, default=0, choices=range(5))
    parser.add_argument('--iterations', type=int, default=3, choices=range(5))
    parser.add_argument('--shots', type=int, default=512)
    args = parser.parse_args()
    backend = BasicSimulator()
    main(args.scenario, args.iterations, args.shots)
