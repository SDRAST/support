Version 1.2.0

Package to provide extended functions for various objects and modules.

View HTML pages [here](https://github.jpl.nasa.gov/pages/RadioAstronomy/support)

### File names

It is dangerous to use here names which are also package names.  For example,
in `support/ephem.py` the statement `from ephem import` will cause the module
to import from itself.  So we call the module `support/Ephem.py`.

### Submodules

The `tests` and `pyro/pyro4_support` subdirectories are git submodules
corresponding to the `tests-support` and `pyro-support` packages.

To pull these submodules, do the following:

```
me@local:/path/to/support$ git submodule init --recursive
me@local:/path/to/support$ git submodule update --recursive --remote
```
