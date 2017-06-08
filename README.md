Package to provide extended functions for various objects and modules.

View HTML pages [here](https://github.jpl.nasa.gov/pages/RadioAstronomy/support)

### File names

It is dangerous to use here names which are also package names.  For example,
in `support/ephem.py` the statement `from ephem import` will cause the module
to import from itself.  So we call the module `support/Ephem.py`.

