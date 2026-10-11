"""Connect independently compiled search with exact reference and explanations."""
from policy_lab.classical import (
    bitstring_to_assignment, enumerate_violations, evaluate_assignment,
    explain_violation,
)
from policy_lab.execution import run_search
from policy_lab.fixtures import get_scenario
from policy_lab.quantum import build_search_circuit

SCENARIO_CHOICES = (
    'contractor_access', 'contractor_access_corrected', 'asymmetric',
    'multiple_solution', 'overlapping_or',
)


def run_experiment(backend, scenario_choice=0, iterations=3, shots=512):
    if type(scenario_choice) is not int or not 0 <= scenario_choice < len(SCENARIO_CHOICES):
        raise ValueError('Scenario choice must be an integer from 0 through 4.')
    if type(shots) is not int or not 1 <= shots <= 4096:
        raise ValueError('Shots must be an integer from 1 through 4096.')
    scenario = get_scenario(SCENARIO_CHOICES[scenario_choice])
    # Builder takes only rules and the user's explicit iteration count.
    spec = build_search_circuit(scenario, iterations)
    reference = enumerate_violations(scenario)
    print('CURRENT EXECUTION — synthetic educational access-control model')
    print('C=contractor, R=project responsible, D=managed device, M=MFA completed')
    print(f"Scenario: {scenario['id']}; display order: C R D M")
    print(f"Permission (OR of AND clauses): {scenario['allow_any']}")
    print(f"Forbidden (OR of AND clauses): {scenario['forbid_any']}")
    print('Violation = permission AND forbidden. All 16 assignments are valid in this model.')
    print(f'Grover iterations: {iterations}. Fixed/user-selected; no automatic solution-count tuning.')
    print('Default 3 iterations is a teaching setting for the known one-of-16 fixture; '
          'it is not optimal for every scenario. Choose 0 for uniform sampling.')
    print(f"Exact classical reference: {reference['violation_count']} / {reference['total_assignments']} violations.")
    execution = run_search(spec, backend, shots)
    candidates = []
    violation_shots = 0
    for bits, count in sorted(execution['counts'].items()):
        assignment = bitstring_to_assignment(scenario, bits)
        verdict = evaluate_assignment(scenario, assignment)
        if verdict['violation']:
            violation_shots += count
        explanation = explain_violation(scenario, assignment)
        candidates.append({'bits': bits, 'assignment': assignment, 'count': count,
                           **verdict, 'explanation': explanation})
        values = ', '.join(f'{a}={str(v).lower()}' for a, v in assignment.items())
        print(f'{bits}: {count} shots; {values}. {explanation}')
    observed = violation_shots / execution['shots_observed']
    uniform = reference['violation_count'] / reference['total_assignments']
    conclusion = (
        'Exhaustive classical verification found no violations within this model.'
        if reference['violation_count'] == 0 else
        f'Classically verified sampled violations: {violation_shots} / {execution["shots_observed"]} shots.'
    )
    print(conclusion)
    print(f'Observed violation proportion: {observed:.2%}; exact uniform reference: {uniform:.2%}.')
    print('Sampling frequencies fluctuate. Failure to sample a violation is not proof of absence. '
          'Simulator runs do not establish practical quantum advantage.')
    return {
        'result_kind': 'current_execution', 'scenario': scenario,
        'classical_reference': reference, 'execution': execution,
        'candidates': candidates, 'observed_violation_proportion': observed,
        'uniform_reference_probability': uniform, 'conclusion': conclusion,
        'total_qubits': spec['total_qubits'],
        'iteration_selection': 'Fixed/user-selected; default 3 reflects known one-of-16 teaching fixture.',
    }
