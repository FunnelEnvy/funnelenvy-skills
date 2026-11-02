"""Unit tests for the live-layer write guard and ID ledger in `_tests/helpers.py`.

A stub stands in for `urllib.request.urlopen`, so no case opens a socket.
G1 to G5 check which calls the guard lets out, and C1 and C2 check the cleanup
the ledger registers. The cases come from fe-sys-hq's _tests v2.0.0.

The helpers are reached as `helpers.<name>` at call time, so each case fails
on its own when a helper is missing rather than the whole module failing to
import.
"""

import unittest
import urllib.request

from _tests import helpers


_TARGET = 'list-declared'


def _classify(method, url):
    """Map a stub request to a create target or a written ID, else None."""
    if method == 'POST' and url.startswith('https://svc/list/'):
        return ('create', url.rsplit('/', 1)[-1])
    if url.startswith('https://svc/item/'):
        return ('write', url.rsplit('/', 1)[-1])
    return None


class _Stub:
    """Record every request that reaches the outbound call."""

    def __init__(self):
        self.calls = []

    def __call__(self, request, *args, **kwargs):
        if isinstance(request, str):
            self.calls.append(('URL', request))
        else:
            self.calls.append((request.get_method(), request.full_url))
        return 'sent'


def _req(method, url):
    return urllib.request.Request(url, method=method)


def _run_inner(body):
    """Run `body(test_case)` as its own test and return the TestResult.

    The host class is built here rather than at module level, so discovery
    never collects it as a test of its own.
    """
    class _Inner(unittest.TestCase):
        def runTest(self):
            body(self)

    result = unittest.TestResult()
    _Inner().run(result)
    return result


class TestLiveWriteGuard(unittest.TestCase):

    def setUp(self):
        self.stub = _Stub()
        self.guard = helpers.LiveWriteGuard([_TARGET], _classify)
        self.call = self.guard.wrap(self.stub)

    def test_permitted_calls_reach_the_outbound_call(self):
        """G1: a read, a declared create and a write on a recorded ID go out."""
        self.guard.record(self, 'item-1', lambda item_id: None)
        self.call(_req('GET', 'https://svc/item/other'))
        self.call(_req('POST', f'https://svc/list/{_TARGET}'))
        self.call(_req('PUT', 'https://svc/item/item-1'))
        self.assertEqual(self.stub.calls, [
            ('GET', 'https://svc/item/other'),
            ('POST', f'https://svc/list/{_TARGET}'),
            ('PUT', 'https://svc/item/item-1'),
        ])

    def test_create_in_undeclared_target_is_refused_before_the_call(self):
        """G2: a create outside the declared targets never leaves the process."""
        with self.assertRaisesRegex(AssertionError, 'list-other'):
            self.call(_req('POST', 'https://svc/list/list-other'))
        self.assertEqual(self.stub.calls, [])

    def test_write_on_unrecorded_id_is_refused_before_the_call(self):
        """G3: a write on an ID the test did not record never leaves the process."""
        with self.assertRaisesRegex(AssertionError, 'item-foreign'):
            self.call(_req('DELETE', 'https://svc/item/item-foreign'))
        self.assertEqual(self.stub.calls, [])

    def test_unrecognized_write_is_refused_before_the_call(self):
        """G4: a write the mapping does not recognize fails closed."""
        with self.assertRaises(AssertionError):
            self.call(_req('POST', 'https://svc/unmapped'))
        self.assertEqual(self.stub.calls, [])

    def test_call_carrying_data_is_checked_as_a_post(self):
        """G5: data passed beside the request makes it a write, refused here."""
        url = 'https://svc/item/item-foreign'
        for call in (lambda: self.call(url, b'{}'),
                     lambda: self.call(url, data=b'{}'),
                     lambda: self.call(urllib.request.Request(url), b'{}')):
            with self.assertRaisesRegex(AssertionError, 'item-foreign'):
                call()
        self.assertEqual(self.stub.calls, [])


class TestLiveWriteGuardCleanup(unittest.TestCase):

    def test_recorded_ids_are_deleted_newest_first_after_a_failure(self):
        """C1: recording an ID registers its delete, and a failed test still runs it."""
        deleted = []
        guard = helpers.LiveWriteGuard([_TARGET], _classify)

        def body(case):
            guard.record(case, 'first', deleted.append)
            guard.record(case, 'second', deleted.append)
            case.fail('inner test fails after recording')

        result = _run_inner(body)
        self.assertEqual(len(result.failures), 1)
        self.assertEqual(deleted, ['second', 'first'])

    def test_failed_delete_is_reported_naming_the_id(self):
        """C2: a delete that raises surfaces as a test problem naming the item."""
        guard = helpers.LiveWriteGuard([_TARGET], _classify)

        def refuse(item_id):
            raise RuntimeError('service said no')

        result = _run_inner(lambda case: guard.record(case, 'left-behind', refuse))
        problems = result.failures + result.errors
        self.assertEqual(len(problems), 1)
        self.assertIn('left-behind', problems[0][1])


if __name__ == '__main__':
    unittest.main()
