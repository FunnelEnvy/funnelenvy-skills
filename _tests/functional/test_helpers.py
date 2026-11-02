"""Functional tests for the live-layer opt-in check in `_tests/helpers.py`.

Each case writes a `.env` into a `tempfile` directory passed as the repo root.
O1 to O3 check when a live module may run. The cases come from fe-sys-hq's
_tests v2.0.0.

The helper is reached as `helpers.live_opt_in_skip_reason` at call time, so
each case fails on its own when the helper is missing.
"""

import os
import tempfile
import unittest
from unittest import mock

from _tests import helpers


_VAR = 'FE_LIVE_TESTS'


class TestLiveOptInSkipReason(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = self._tmp.name

    def _write_env(self, text):
        with open(os.path.join(self.root, '.env'), 'w', encoding='utf-8') as f:
            f.write(text)

    def test_unset_variable_returns_a_skip_reason(self):
        """O1: a default run, with the variable unset, skips."""
        env = {k: v for k, v in os.environ.items() if k != _VAR}
        with mock.patch.dict(os.environ, env, clear=True):
            reason = helpers.live_opt_in_skip_reason(_VAR, self.root)
        self.assertIsInstance(reason, str)
        self.assertIn(_VAR, reason)

    def test_opt_in_listed_in_dotenv_skips_naming_dotenv(self):
        """O2: a persisted opt-in in `.env` never turns a run live."""
        self._write_env(f'OTHER=x\n{_VAR}=1\n')
        with mock.patch.dict(os.environ, {_VAR: '1'}):
            before = dict(os.environ)
            reason = helpers.live_opt_in_skip_reason(_VAR, self.root)
            after = dict(os.environ)
        self.assertIsInstance(reason, str)
        self.assertIn('.env', reason)
        self.assertEqual(before, after)

    def test_opt_in_from_run_environment_only_returns_none(self):
        """O3: an opt-in set only in the run's environment goes live."""
        self._write_env('OTHER=x\n')
        with mock.patch.dict(os.environ, {_VAR: '1'}):
            reason = helpers.live_opt_in_skip_reason(_VAR, self.root)
        self.assertIsNone(reason)


if __name__ == '__main__':
    unittest.main()
