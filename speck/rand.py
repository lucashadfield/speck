__all__ = ['IntRandomiser', 'FloatRandomiser', 'SelectionRandomiser']

import random
import inspect
from functools import wraps
from typing import Callable, Iterable

from functools import lru_cache


def randargs(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        def unpack(x):
            if isinstance(x, ArgumentRandomiser):
                return x()
            elif isinstance(x, Iterable) and not isinstance(x, str):
                return type(x)([unpack(i) for i in x])
            else:
                return x

        args = [unpack(a) for a in args]
        kwargs = {k: unpack(v) for k, v in kwargs.items()}

        setattr(
            wrapper, 'last_call', [args[1:], kwargs] if len(args[1:]) else kwargs,
        )

        return fn(*args, **kwargs)

    wrapper.last_call = None

    return wrapper


class ArgumentRandomiser(random.Random):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(x=kwargs.get('seed'))

    @staticmethod
    def _make_callable(x):
        if isinstance(x, Callable):
            return x
        return lambda: x

    def __call__(self):
        raise NotImplementedError

    def __repr__(self):
        d = [f'{k}={v}' for k, v in self.__dict__.items() if not k.startswith('_')]
        return f'{self.__class__.__name__}({", ".join(d)})'


class IntRandomiser(ArgumentRandomiser):
    def __init__(self, low, high, size=None, ordered=True, **kwargs):
        self.low = self._make_callable(low)
        self.high = self._make_callable(high)
        self.size = self._make_callable(size)
        self.ordered = self._make_callable(ordered)
        super().__init__(**kwargs)

    def __call__(self):
        low = self.low()
        high = self.high()
        size = self.size()

        if size is None:
            return self.randint(low, high)

        ret = self.choices(range(low, high + 1), k=size)
        if self.ordered():
            return tuple(sorted(ret)[:: -1 if low > high else 1])
        return tuple(ret)


class FloatRandomiser(ArgumentRandomiser):
    def __init__(self, low, high, size=None, dp=3, ordered=True, **kwargs):
        self.low = self._make_callable(low)
        self.high = self._make_callable(high)
        self.size = self._make_callable(size)
        self.dp = self._make_callable(dp)
        self.ordered = self._make_callable(ordered)
        super().__init__(**kwargs)

    def __call__(self):
        low = self.low()
        high = self.high()
        size = self.size()
        dp = self.dp()

        if size is None:
            return round(self.uniform(low, high), dp)

        ret = [round(self.uniform(low, high), dp) for _ in range(size)]
        if self.ordered():
            return tuple(sorted(ret)[:: -1 if low > high else 1])
        return tuple(ret)


class SelectionRandomiser(ArgumentRandomiser):
    def __init__(self, source, size=None, replacement=False, **kwargs):
        self.source = self._make_callable(source)
        self.size = self._make_callable(size)
        self.replacement = self._make_callable(replacement)
        super().__init__(**kwargs)

    def __call__(self, *args, **kwargs):
        source = self.source()
        size = self.size()

        if size is None:
            return self.choice(source)

        if self.replacement():
            return tuple(self.choices(source, k=size))
        else:
            return tuple(self.sample(source, k=size))
