import datetime
import types
import time

import pytz

__all__ = ["ControlFlowMixin"]


def _null_condition_factory():

    def null_condition():
        return False

    return null_condition


def _time_condition_factory(when=None):

    def time_condition():
        if when is None:
            return True
        now = ControlFlowMixin.now()
        if now >= when:
            return True
        else:
            return False

    return time_condition


def _condition_factory(cond=None):

    if callable(cond):
        condition = [cond]
    elif not hasattr(cond, "append"):
        condition = [_time_condition_factory(cond)]
    else:
        condition = cond

    return condition


class _DelayedCall(object):

    def __init__(self, start=None, condition=None):
        self.condition = condition
        self.start = start

    def _wait_for_start(self, timeout=1.0):
        """
        Block until start time is reached.
        """
        if self.start is None:
            return
        else:
            now = ControlFlowMixin.now()
            while now < self.start:
                now = ControlFlowMixin.now()
                time.sleep(timeout)
                yield self.start - now

    def _eval_condition(self):
        if self.condition is not None:
            cond_val = [c() for c in self.condition]
        else:
            cond_val = [False]
        return all(cond_val)

    def wait(self, timeout=1.0):

        def _wait():
            while True:
                yield
                time.sleep(timeout)

        for e in self.run(_wait):
            yield e

    def run(self, generator_func):
        """
        """
        def _run():
            for e in self._wait_for_start():
                yield e

            if not isinstance(generator_func, types.GeneratorType):
                generator = generator_func()
            else:
                generator = generator_func

            if self._eval_condition():
                return

            for val in generator:
                if self._eval_condition():
                    return
                else:
                    yield val

        for e in _run():
            yield e

    def loop(self, generator_func, iterations=None):
        """
        """
        def _loop():

            if isinstance(generator_func, types.GeneratorType):
                for e in self.run(generator_func):
                    yield e
                return

            for e in self._wait_for_start():
                yield e

            def while_cond(idx):
                if iterations is None:
                    return True
                else:
                    return idx < iteration

            def update(idx):
                if iterations is None:
                    return idx
                else:
                    return idx + 1

            loop_var = 0

            if self._eval_condition():
                return

            while while_cond(loop_var):
                generator = generator_func()
                for val in generator:
                    if self._eval_condition():
                        return
                    else:
                        yield val
                loop_var = update(loop_var)

        for e in _loop():
            yield e

    def at(self, when):
        self.start = when
        return self

    def until(self, cond=None):
        cond = _condition_factory(cond)
        self.condition = cond
        return self


class ControlFlowMixin(object):
    """
    Mixin class for controlling when and until when functions are called.
    Examples assume this class has been mixed into some child class:

    .. code-block:: python

        MixedIn(ControlFlowMixin):
            pass

        mixed_in = MixedIn()

    Attributes:
        tz (pytz.timezone): timezone. Defaults to UTC
    """

    tz = pytz.timezone("UTC")

    def next_up(self):
        """
        Return an empty _DelayedCall instance.
        """
        return _DelayedCall()

    def until(self, cond=None):
        """
        Run some generator until some condition, or list of conditions is met.

        Examples:

        Say we have some function ``runner`` defined as follows:

        .. code-block:: python

            def runner():
                print("runner called")
                yield

        We can use until in a variety of ways:

        .. code-block:: python

            import datetime
            import random

            # run until runner is complete, or for next 5 seconds,
            # which ever comes first
            for e in mixed_in.until(
                MixedIn.now() + datetime.timedelta(seconds=5)).run(runner):
                yield e

            # run until the following function evaluates to True

            def condition_factory():
                def condition():
                    rand = random.random()
                    if rand > 0.5:
                        return True
                    return False
                return condition

            for e in mixed_in.until(condition_factory()).run(runner):
                yield e

            # we can pass a list of conditions if we want:

            for e in mixed_in.until(
                [condition_factory(), condition_factory()]).run(runner):
                yield e

        Args:
            cond (list/callable/datetime.datetime): List of callables that
                return booleans, a single boolean-returning callable, or
                a datetime.datetime object. If the latter is passed, the
                resulting _DelayedCall object will run, loop, or wait until
                the specified time.
        Returns:
            _DelayedCall
        """
        cond = _condition_factory(cond=cond)
        return _DelayedCall(condition=cond)

    def at(self, when):
        """
        Created a _DelayedCall instance that will run or loop at a
        specified time.

        Examples:

        .. code-block:: python

            def runner():
                yield

            for e in mixed_in.at(
                MixedIn.now() + datetime.timedelta(seconds=5)).run(runner):
                yield e

        Args:
            when (datetime.datetime): timezone aware datetime object indicating
                when to _DelayedCall methods.
        Returns:
            _DelayedCall
        """
        cond = [_null_condition_factory()]
        return _DelayedCall(condition=cond, start=when)

    @classmethod
    def now(cls):
        """
        Returns:
            datetime.datetime: timezone aware datetime object
        """
        return datetime.datetime.utcnow().replace(tzinfo=cls.tz)
