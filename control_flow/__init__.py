import datetime
import types
import time

import pytz

__all__ = ["ControlFlowMixin"]

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

            for val in generator:
                if self.condition is not None:
                    cond_val = [c() for c in self.condition]
                else:
                    cond_val = [True]

                if not all(cond_val):
                    return
                else:
                    yield val

        for e in _run():
            yield e

    def loop(self, generator_func, iterations=None):
        """
        """
        def _loop():
            for e in self._wait_for_start():
                yield e

            if iterations is None:
                while_cond = lambda idx: True
                update = lambda idx: idx
            else:
                while_cond = lambda idx: idx < iterations
                update = lambda idx: idx + 1
            loop_var = 0

            while while_cond(loop_var):
                generator = generator_func()
                for val in generator:
                    if self.condition is not None:
                        cond_val = [c() for c in self.condition]
                    else:
                        cond_val = [True]
                    if not all(cond_val):
                        return
                    else:
                        yield val
                loop_var = update(loop_var)

        for e in _loop():
            yield e

class ControlFlowMixin(object):

    tz = pytz.timezone("UTC")

    def _null_condition_factory(self):

        def null_condition():
            return True

        return null_condition

    def _time_condition_factory(self, when=None):

        def time_condition():
            if when is None:
                return True
            now = self.now()
            if now >= when:
                return False
            else:
                return True

        return time_condition

    def _condition_factory(self, cond=None):

        if callable(cond):
            condition = [cond]
        elif not hasattr(cond, "append"):
            condition = [self._time_condition_factory(cond)]
        else:
            condition = cond

        return condition

    # def run(self, *args, **kwargs):
    #     return _DelayedCall().run(*args, **kwargs)

    def until(self, cond=None):
        """
        Run some generator until some condition, or list of conditions is met.

        Args:
            cond (list/callable/datetime.datetime):
        """
        cond = self._condition_factory(cond=cond)
        return _DelayedCall(condition=cond)

    def at(self, when):
        """
        """
        cond = [self._null_condition_factory()]
        return _DelayedCall(condition=cond, start=when)

    @classmethod
    def now(cls):
        return datetime.datetime.utcnow().replace(tzinfo=cls.tz)
