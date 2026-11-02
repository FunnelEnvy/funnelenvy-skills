"""Shared test helpers: the live-layer opt-in check and write guard.

`_tests/CLAUDE.md` `Live Tests` governs their use.
"""

import os


def live_opt_in_skip_reason(var_name, repo_root):
    """Return why a live-layer module must skip, or None when it may run.

    A live module runs only when `var_name` is `1` in `os.environ` and the
    repo root's `.env` does not list `var_name`. The `.env` check reads the
    file directly, because a loader may already have copied its keys into
    `os.environ`, where they look the same as a value the run set. Three
    outcomes:

    - `.env` under `repo_root` lists `var_name`: a reason naming `.env`,
      whatever `os.environ` holds.
    - `var_name` is not `1` in `os.environ`: a reason naming the variable.
    - Otherwise: None.

    Never writes `os.environ`. `_tests/CLAUDE.md` `Live Tests` owns when an
    agent may set the variable.
    """
    env_path = os.path.join(str(repo_root), '.env')
    if os.path.isfile(env_path):
        with open(env_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('export '):
                    line = line[len('export '):].lstrip()
                if (line and not line.startswith('#') and '='
                        in line and line.split('=', 1)[0].strip() == var_name):
                    return (f'{var_name} is listed in {env_path}; set it only '
                            f"in the live run's own environment")
    if os.environ.get(var_name) != '1':
        return f'{var_name} is not set to 1; live tests run only on opt-in'
    return None


def _request_method_and_url(request, data=None):
    """Return the `(method, url)` that `urlopen(request, data)` would send.

    A URL string is a `POST` when `data` is given and a `GET` otherwise. A
    `urllib.request.Request` keeps its explicit method; without one it is a
    `POST` when it or the call carries data, as `urlopen` sends it.
    """
    if isinstance(request, str):
        return ('POST' if data is not None else 'GET'), request
    method = getattr(request, 'method', None)
    if not method:
        has_data = data is not None or request.data is not None
        method = 'POST' if has_data else 'GET'
    return method.upper(), request.full_url


class LiveWriteGuard:
    """Refuse live-test writes outside declared targets and recorded IDs.

    Built from the create targets a test declares and a `classify(method,
    url)` mapping. The mapping returns `('create', target)`, `('write',
    item_id)`, or None for a request it does not recognize.

    `wrap(call)` returns a stand-in for the outbound call function. Each
    request is checked before `call` runs, with the method `urlopen` would
    send: a URL string or a method-less `Request` called with data is a
    `POST`.

    - `GET` or `HEAD`: passes, without consulting the mapping.
    - A create: passes only into a declared target.
    - A write: passes only on an ID passed to `record`.
    - Anything else, an unrecognized request included: raises
      `AssertionError` naming the request, target or ID. `call` is never
      reached.

    `record(test_case, item_id, delete)` adds the ID to the ledger and
    registers `delete(item_id)` with `test_case.addCleanup`, so recorded
    items are deleted newest first, after a failure as well as a pass. A
    delete that raises is re-raised as `AssertionError` naming the ID.
    """

    def __init__(self, create_targets, classify):
        self.create_targets = frozenset(create_targets)
        self.classify = classify
        self.recorded = set()

    def check(self, request, data=None):
        """Raise AssertionError when `request` may not go out; else return None.

        `data` is the body the outbound call was given alongside `request`.
        """
        method, url = _request_method_and_url(request, data)
        if method in ('GET', 'HEAD'):
            return
        verdict = self.classify(method, url)
        if verdict is None:
            raise AssertionError(
                f'live guard refused {method} {url}: the mapping does not '
                f'recognize it')
        kind, key = verdict
        if kind == 'create':
            if key not in self.create_targets:
                raise AssertionError(
                    f'live guard refused {method} {url}: create target '
                    f'{key!r} is not declared')
        elif kind == 'write':
            if key not in self.recorded:
                raise AssertionError(
                    f'live guard refused {method} {url}: ID {key!r} was not '
                    f'created by this test')
        else:
            raise AssertionError(
                f'live guard refused {method} {url}: unknown mapping verdict '
                f'{kind!r}')

    def wrap(self, call):
        """Return `call` behind the guard's check."""
        def guarded(request, *args, **kwargs):
            data = args[0] if args else kwargs.get('data')
            self.check(request, data)
            return call(request, *args, **kwargs)
        return guarded

    def record(self, test_case, item_id, delete):
        """Record `item_id` as created and register its delete as a cleanup."""
        self.recorded.add(item_id)
        test_case.addCleanup(self._delete, item_id, delete)

    @staticmethod
    def _delete(item_id, delete):
        try:
            delete(item_id)
        except (Exception, SystemExit) as exc:
            raise AssertionError(
                f'live cleanup could not delete {item_id!r}; it may be left '
                f'behind: {exc!r}') from exc
