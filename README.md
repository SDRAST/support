Version 1.2.0

Package to provide extended functions for various objects and modules.

View HTML pages [here](https://SDRAST.github.com/support)

### File names

It is dangerous to use here names which are also package names.  For example,
in `support/ephem.py` the statement `from ephem import` will cause the module
to import from itself.  So we call the module `support/Ephem.py`.

### Submodules

The `test`, `pyro` and `trifeni` subdirectories are git submodules
corresponding to the `support_test`, `support_pyro`, and `trifeni` packages.

To pull these submodules, do the following:

```
me@local:/path/to/support$ git submodule init --recursive
me@local:/path/to/support$ git submodule update --recursive --remote
```

### Testing

Note that the testing directory is `tests`, not `test`. The latter corresponds
to the `support_test` submodule. Most of the subpackages have their own tests,
so these are designed to determine whether packages can be imported or not.

```
/path/to/support$ python -m unittest discover -s tests -t .
```
