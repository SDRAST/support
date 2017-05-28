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