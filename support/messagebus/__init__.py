"""
Pyro MessageBus:  a simple pub/sub message bus.
Provides a way of cummunicating where the sender and receivers are fully decoupled.

Pyro - Python Remote Objects.  Copyright by Irmen de Jong (irmen@razorvine.net).
"""

PYRO_MSGBUS_NAME = "Pyro.MessageBus"
from messagebus import make_messagebus, MessageBus, Subscriber
from messagebus_thread import MessageBusThread
