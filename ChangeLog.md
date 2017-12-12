## RA support Change log

### Version 1.1

- Added support for tunneling with Pyro4.
- Using Pyro3 support utilities remains the same.
- Added TAMS_Source, which is an extension of `ephem.FixedBody`.
- Added `process.BasicProcess`, essentially a wrapper over `subprocess.POPEN`, with a kill method
- Added threading utilties, namely a `threading.Thread` extension that allows for pausing and stopping.
- Added a messagebus, a Pyro4 mechanism for publishing and subscribing.
- Added a new logging module method. This has some overlap with existing methods, and needs to be consolidated in
future versions.

### Version 1.2

- Moved `test` and `pyro/pyro4*` to `deprecated`. Instead of using these modules
the package now attempts to use the maintained `pyro_support` and `tests_support`
packages.
- Moved `Ephem.py` to a sub package. The `Ephem` package has all the same imports,
except things are structured in a manner such that it is easier to see where
individual chunks of code live.
