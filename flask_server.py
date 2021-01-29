"""
flask_server provides the FlaskServer class

FlaskServer is a superclass for any server that wants to be able to provide a
web service using flask
"""
import inspect    # used by flaskify_io
import logging
import os
import signal     # used by server to handle signals
import threading  # allows server to be threaded
import time
import datetime

module_logger = logging.getLogger(__name__)


__all__ = ["FlaskServer"]

class FlaskServer(object):
    """
    class that can launch an object or instance of class on a nameserver or
    simply as a daemon.

    The flaskify method can automatically create flask routes from an object's
    methods

    The flaskify_io method can automatically create socket routes from an object's
    methods.

    Attributes:
        logger (logging.getLogger): object logger
        cls (type): a class whose methods and attribute the server accesses by
            instantiating an object.
        obj (object): An object whose methods and attributes the server accesses.
        name (str): Name of server
        logfile (str): Path to logfile for server.
        running (bool): boolean expressing whether the server has been launched
            or not
        tunnel (support.trifeni.Pyro5Tunnel like): A tunnel instance.
        tunnel_kwargs (dict): key word arguments that are uesd to instantiate
            tunnel instance
        server_uri (str/Pyro5.URI): the server's URI
        daemon_thread (threading.Thread): the thread in which the daemon's
            requestLoop method is running.
        daemon (Pyro5.Daemon): The server's daemon.
        threaded (bool): Whether or not the server is running in a thread or
            on the main thread.
        lock (threading.Lock): Lock for thread safety.
    """
    def __init__(self, cls=None,
                       obj=None,
                       cls_args=None,
                       cls_kwargs=None,
                       name=None,
                       logfile=None,
                       logger=None,
                       **kwargs):
        """

        Args:
            cls (type, optional): A class that will be instantiated with cls_args
                cls_kwargs, to be used as the server's object.
            obj (object, optional): Some object that will be registered on a Pyro5.Daemon.
            cls_args (tuple/list, optional): Arguments passed to cls.
            cls_kwargs (dict, optional): Keyword Arguments passed to cls.
            name (str, optional): server name
            logfile (str, optional): path to server's logfile
            logger (logging.getLogger, optional): logging instance.
            kwargs: Passed to super class.
        """
        if not logger:
            logger = module_logger.getChild(self.__class__.__name__)
        self.logger = logger
        self.logger.debug("Pyro5Server:__init__: cls: {}".format(cls))
        if obj is None and cls is None:
            msg = "Need to provide either an object or a class to __init__"
            self.logger.error(msg)
            raise RuntimeError(msg)

        self.cls = None
        self.obj = None

        if obj is not None:
            self.obj = obj

        if cls is not None:
            self.cls = cls
            if cls_args is None:
                cls_args = ()
            if cls_kwargs is None:
                cls_kwargs = {}
            try:
                self.obj = self._instantiate_cls(cls, *cls_args, **cls_kwargs)
            except Exception as err:
                pass

        if name is None:
            name = self.obj.__class__.__name__
        self._name = name
        self._logfile = logfile

        self._running = False
        self.tunnel_kwargs = None
        self.server_uri = None
        self.daemon_thread = None
        self.daemon = None
        self.threaded = False
        self.lock = threading.Lock()

    def _instantiate_cls(self, cls, *args, **kwargs):
        """
        Create an instance of a class, given some arguments and keyword arguments.

        Args:
            cls (type): a class to be instantiated
            args: passed to cls
            kwargs: passed to cls
        """
        return cls(*args, **kwargs)

    @property
    def logfile(self):
        """Make logfile attribute accessible to a proxy corresponding to this server."""
        return self._logfile

    def running(self):
        """Get running status of server"""
        with self.lock:
            return self._running

    @property
    def name(self):
        """
        Make name attribute accessible to a proxy.
        """
        return self._name

    @name.setter
    def name(self, new_name):
        """
        Set name attribute.
        """
        self._name = new_name

    def ping(self):
        """
        ping the server
        """
        return "hello"

    def close(self):
        """
        Close down the server.
        If we're running this by itself, this gets called by the signal handler.
        """
        with self.lock:
            self._running = False
            try:
                self.daemon.unregister(self.obj)
            except Exception as err:
                self.logger.error(
                 "close: Couldn't unregister {} from daemon: {}".format(self.obj, err))

            if self.threaded:
                self.daemon.shutdown()
            else:
                self.daemon.close()

    @classmethod
    def flaskify(cls, *args, **kwargs):
        """
        Create a flask server using the PyroServer.
        There are two use cases:
        You pass parameters to instantiate a new instance of cls, or
        You pass an object of cls as the first argument, and this is the server
        used.

        Args:
            args (list/tuple): If first argument is an object, then register
                this object's exposed methods. Otherwise, use args and kwargs
                as parameters to instantiate an object of implicit cls.
            kwargs (dict): Passed to implicit cls.
        Returns:
            tuple:
                * app (Flask): Flask app
                * server (object): some object whose methods/attributes have been
                  registered as routes on app.
        """
        import json
        from flask import Flask, jsonify, request
        from flask_socketio import SocketIO, send, emit

        app = kwargs.pop("app", None)

        if len(args) > 0:
            if isinstance(args[0], cls):
                server = args[0]
        else:
            server = cls(*args, **kwargs)
        if app is None:
            app = Flask(server.name)

        @app.route("/<method_name>", methods=['GET'])
        def method(data):
            try:
                get_data = json.loads(list(request.args.keys())[0])
            except json.decoder.JSONDecodeError:
                get_data = request.args
            args = get_data.get('args', ())
            kwargs = get_data.get('kwargs', {})
            if not (isinstance(args, list) or isinstance(args, tuple)):
                args = [args]
            if method_name in cls.__dict__:
                method = getattr(server, method_name)
                exposed = getattr(method, "_pyroExposed", None)
                if exposed:
                    status = "method {}._pyroExposed: {}".format(method_name, exposed)
                    try:
                        result = method(*args, **kwargs)
                    except Exception as err:
                        status = status + "\n" + str(err)
                        result = None
                else:
                    status = "method {} is not exposed".format(method_name)
                    result = None
            else:
                status = "method {} is not an server method".format(method_name)
                result = None
            return jsonify(data={"status":status, "result":result})

        return app, server

    @classmethod
    def flaskify_io(cls, *args, **kwargs):
        """
        Create a flaskio server.
        Use case is the same as Pyro5Server.flaskify, except that instead of
        registering an object's methods/attributes as routes, it registers
        them as socket routes.

        Args:
            args (list/tuple): If first argument is an object, then register
                this object's exposed methods. Otherwise, use args and kwargs
                as paramters to instantiate an object of implicit cls.
            kwargs (dict): Passed to implicit cls.

        Returns:
            tuple:
                * app (Flask): Flask app
                * socketio (SocketIO): flask_socketio.SocketIO instance.
                * server (object): object whose methods have been registered as socket routes.
        """
        import json
        from flask import Flask, jsonify, request
        from flask_socketio import SocketIO, send, emit
        import eventlet

        socketio = kwargs.pop("socketio", None)
        app = kwargs.pop("app", None)

        if len(args) > 0:
            if isinstance(args[0], cls):
                server = args[0]
        else:
            server = cls(*args, **kwargs)

        server.logger.info("Making flask socketio app.")
        if app is None:
            app = Flask(server.name)
            app.config['SECRET_KEY'] = "radio_astronomy_is_cool"
        if socketio is None:
            socketio = SocketIO(app, async_mode="eventlet")

        for method_pair in inspect.getmembers(cls):
            method_name = method_pair[0]
            method = getattr(server, method_name)
            exposed = getattr(method, "_pyroExposed", None)
            pasync = getattr(method, "_pyroAsync", None)
            if exposed:
                server.logger.info("flaskify_io: Registering method: {}, pasync: {}".format(
                                                           method_name, pasync))
                def wrapper(method, method_name):
                    def inner(data):
                        args = data.get("args", [])
                        kwargs = data.get("kwargs", {})
                        pasync = getattr(method, "_pyroAsync", None)
                        # server.logger.debug("{}: pasync: {}".format(method_name, pasync))
                        # server.logger.debug("{}: kwargs: {}".format(method_name, kwargs))
                        # server.logger.debug("{}: args: {}".format(method_name, args))
                        try:
                            if pasync:
                                kwargs['socket_info'] = {'app':app, 'socketio':socketio}
                                g = eventlet.spawn_n(method, *args, **kwargs)
                                status = "eventlet.spawn_n started"
                                result = None
                            else:
                                result = method(*args, **kwargs)
                                status = "success"
                        except Exception as err:
                            result = None
                            status = str(err)
                            server.logger.error(status)
                        with app.test_request_context("/"):
                            socketio.emit(method_name, {"status":status, "result":result})
                    return inner

                # socketio.on(method_name)(wrapper(method, method_name))
                socketio.on_event(method_name, wrapper(method, method_name))

        return app, socketio, server

