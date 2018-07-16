from __future__ import print_function
import logging
import inspect


__all__ = [
    "get_help"
]

module_logger = logging.getLogger(__name__)


def _get_prop_doc(prop):
    name = prop.fget.__name__
    doc = prop.__doc__.strip()
    return "{}:\n\t{}".format(name, doc)


def _get_method_doc(method, method_type="instance"):
    name = method.__name__
    spec = inspect.getargspec(method)
    args_doc = []
    keyword_args_doc = []
    if spec.defaults is not None:
        for default in spec.defaults[::-1]:
            keyword_arg = spec.args.pop(-1)
            keyword_args_doc.append(
                "{}={}".format(keyword_arg, default)
            )
        keyword_args_doc = keyword_args_doc[::-1]
    for arg in spec.args:
        args_doc.append(arg)
    args_doc.extend(keyword_args_doc)
    args = ", ".join(args_doc)
    doc = ""
    if method.__doc__ is not None:
        doc = method.__doc__.strip()
    method_doc = "{}({}):\n\t{}".format(name, args, doc)
    if method_type != "instance":
        return "{} {}".format(method_type, method_doc)
    else:
        return method_doc


def get_help(cls):
    """
    generate help text from a class.

    Examples:

    .. code-block::python

        >>> from support.doc_util import get_help
        >>> from support.tests.test_doc_util import TestClass
        >>> print(get_help(TestClass))
        classmethod class_method1(cls, arg1):
                class_method1 documentation
        method1(self):
                method1 documentation
        method2(self, arg1, kwarg0=None):
                method2 documentation
        method3(self):
                method3 documentation
        prop1:
                prop1 documentation
        staticmethod static_method1(arg1):
                static_method1 documentation

    Args:
        cls (type): class whose help text we'd like

    Returns:
        str: help text
    """
    doc = []
    for member_name, member in inspect.getmembers(cls):
        if inspect.ismethod(member):
            if member.__self__ is None:
                doc.append(
                    _get_method_doc(member.__func__))
            else:
                doc.append(
                    _get_method_doc(member.__func__, method_type="classmethod"))
        if inspect.isfunction(member):
            doc.append(_get_method_doc(member, method_type="staticmethod"))
        if isinstance(member, property):
            doc.append(_get_prop_doc(member))

    return "\n".join(doc)
