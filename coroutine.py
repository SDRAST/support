import functools

def coroutine(func):
    """
    Simple decorator to "prime" a coroutine

    Examples:

    .. code-block:: python

        @coroutine
        def my_coroutine():
            while True:
                input = (yield)
                print(input)

        c = my_coroutine() # no need to call next(c)
        c.send("hey")
        c.send("my")
        c.send("name")

    When run, this will produce the following output:

    .. code-block:: none

        hey
        my
        name

    """
    @functools.wraps(func)
    def inner(*args, **kwargs):
        co = func(*args, **kwargs)
        next(co)
        return co

    return inner
