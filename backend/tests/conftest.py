import collections
import pytest


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    from backend.app.core.rate_limit import limiter

    def _reset():
        for value in vars(limiter).values():
            if isinstance(value, (dict, list, set, collections.deque)):
                value.clear()

    _reset()
    yield
    _reset()