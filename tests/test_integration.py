import contextlib
import io
import unittest
from unittest.mock import Mock

from qiskit.providers.basic_provider import BasicSimulator
from qiskit.providers.jobstatus import JobStatus
from policy_lab.application import run_experiment
from policy_lab.execution import decode_counts, run_search
from policy_lab.fixtures import get_scenario
from policy_lab.quantum import build_search_circuit


class IntegrationTests(unittest.TestCase):
    def test_nontrivial_classical_bit_mapping(self):
        self.assertEqual(decode_counts({'0110': 7}, ['C','R','D','M'],
                                      {'C':1,'R':3,'D':0,'M':2}), {'1001':7})

    def test_invalid_counts_and_mapping(self):
        for counts in ({'1 0':1}, {'01':-1}, {'01':True}, {'01':0.5}):
            with self.assertRaises(ValueError):
                decode_counts(counts, ['C','R'], {'C':0,'R':1})
        with self.assertRaises(ValueError):
            decode_counts({}, ['C','R'], {'C':0,'R':0})

    def test_one_job_and_failures(self):
        spec = build_search_circuit(get_scenario('asymmetric'), 0)
        for status, counts in ((JobStatus.DONE, {'1011':8}),
                               (JobStatus.ERROR, {}), (JobStatus.CANCELLED, {}),
                               (JobStatus.DONE, {}), (JobStatus.DONE, {'1011':7})):
            backend = Mock()
            backend.name = 'test_backend'
            backend.run.return_value.status.return_value = status
            backend.run.return_value.result.return_value.get_counts.return_value = counts
            with contextlib.redirect_stdout(io.StringIO()):
                if status == JobStatus.DONE and sum(counts.values()) == 8:
                    self.assertEqual(run_search(spec, backend, 8)['counts'], {'1101':8})
                else:
                    with self.assertRaises(RuntimeError):
                        run_search(spec, backend, 8)
            backend.run.assert_called_once()
            self.assertNotIsInstance(backend.run.call_args.args[0], list)

    def test_all_scenarios_end_to_end(self):
        for choice, expected in enumerate([1,0,1,2,6]):
            with self.subTest(choice=choice), contextlib.redirect_stdout(io.StringIO()):
                report = run_experiment(BasicSimulator(seed_simulator=42), choice, 3, 128)
                self.assertEqual(report['classical_reference']['violation_count'], expected)
                self.assertEqual(sum(c['count'] for c in report['candidates']),128)
                self.assertTrue(all(c['violation'] == (c['allowed'] and c['forbidden'])
                                    for c in report['candidates']))
                if choice in (0,2):
                    self.assertGreater(report['observed_violation_proportion'],0.8)
                if choice == 1:
                    self.assertEqual(report['observed_violation_proportion'],0)
                    self.assertIn('Exhaustive classical verification',report['conclusion'])

    def test_uniform_baseline_and_input_errors(self):
        with contextlib.redirect_stdout(io.StringIO()):
            report = run_experiment(BasicSimulator(seed_simulator=42), 2, 0, 512)
            self.assertLess(report['observed_violation_proportion'],0.15)
            for kwargs in ({'scenario_choice':True}, {'iterations':5}, {'shots':0}):
                with self.assertRaises(ValueError):
                    run_experiment(BasicSimulator(), **kwargs)
