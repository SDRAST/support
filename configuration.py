"""
module configuration - Provides a single file for program parameters

Includes names of directories and files.  Both functions are private, meant to
be used only by software configuration generators.
"""
import os
import datetime

from support.pyro import async

# ----- general classes and functions for managing software configurations ----

def _check_and_create(path):
    """
    Check for path and create if needed
    
    This is a private function.
    """
    if not os.path.exists(path):
        os.makedirs(path)

def _make_properties(prop_names):
    """
    Decorator function for adding public properties to classes
    
    This creates the property, and its getter and setter methods
    
    Dean comments: "_make_properties is a _very esoteric function, and I 
    remember wondering if I should remove it because it decreases readability 
    while saving only a few lines of code. In general, I sort of think class 
    decorators should be used sparingly, as they often obfuscate more than they
    clarify, (I would argue that the Pyro4.expose decorator is an example of a 
    good class decorator.)"
    
    @param prop_names : properties to be defined for the decorated class
    @type  prop_names : list of str
    """
    def property_factory(prop_name):
        """
        local function which returns a getter and setter
        """
        def prop_get(self):
            """
            this defines a method for getting the property's value
            """
            prop_val = getattr(self, "_{}".format(prop_name))
            return prop_val
            
        def prop_set(self, new_val):
            """
            this defines a method for setting the property's value
            """
            setattr(self, "_{}".format(prop_name), new_val)
            
        # return the methods for the named property
        return prop_get, prop_set

    def wrapper(cls):
        """
        Enhances a class by setting the attributes (property_names) passed to 
        the decorator function
        
        @param cls : class to be decorated
        @type  cls : class
        """
        for prop_name in prop_names:
            prop = property(*property_factory(prop_name))
            setattr(cls, prop_name, prop)
        return cls

    return wrapper


class Configuration(object):
    """
    class for creating software configurations
    """
    _protected = {"_emitter", "_config"} # reserved attributes

    def __init__(self, cls, *args, **kwargs):
        """
        Initialize a configuration
        
        The configuration may have an associated event emitter to which
        callbacks (functions to invoke when something changes) can be
        registered.  If the keyword argument "threaded" is not provided then
        there will be no event emitter.
        
        @param cls : class from which a configuration object will be created
        @type  cls : class
        
        @param args : additional positional arguments for initializing 'cls'
        @type  args : list
        
        @param kwargs : keyword arguments for initializing 'cls'
        @type  kwargs : dict
        """
        # create the event emitter
        self._emitter = async.EventEmitter(
            threaded=kwargs.pop("threaded", False)
        )
        # create the configuration
        self._config = cls(*args, **kwargs)

    def __getattr__(self, attr):
        if attr in Configuration._protected:
            return object.__getattr__(self, attr, val)
        elif attr in self._emitter.__class__.__dict__:
            return getattr(self._emitter, attr)
        else:
            # self._emitter.emit(attr)
            return getattr(self._config, attr)

    def __setattr__(self, attr, val):
        if attr in Configuration._protected:
            object.__setattr__(self, attr, val)
        else:
            setattr(self._config, attr, val)
            self._emitter.emit(attr, val)

    def make_today_dir(self, base_dir):
        """
        Make the following directory structure:

        base_dir/<year>/<doy>

        Args:
            base_dir (str):

        Returns:
            str: base_dir with year and doy subdirectories
        """
        year, doy = datetime.datetime.utcnow().strftime("%Y,%j").split(",")
        today_dir = os.path.join(base_dir, year, doy)
        _check_and_create(today_dir)
        return today_dir
        

