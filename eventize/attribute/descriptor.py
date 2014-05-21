# -*- coding: utf8 -*-
from .. import descriptors
from .handler import Handler, Subject, InstanceHandler
from .event import Event

class Value(object):
    def __init__(self, value, instance, alias):
        self.instance = instance
        self.name = alias
        self.cls = getattr(type(instance), alias)
        self.desc = type(self.cls)
        self.on_get = InstanceHandler()
        self.on_set = InstanceHandler()
        self.on_del = InstanceHandler()
        if value is not None:
            self.set(value)

    def get(self):
        event = self.notify('on_get', getattr(self, 'data'))
        return event.returns()

    def set(self, value):
        event = self.notify('on_set', value)
        setattr(self, 'data', event.returns())

    def delete(self):
        event = self.notify('on_del', getattr(self, 'data'))
        delattr(self, 'data')

    def notify(self, event_name, value):
        event = Event(self.instance, name=self.name, value=value)
        getattr(self.desc, event_name)(event)
        getattr(self.cls, event_name)(event)
        getattr(self, event_name)(event)
        return event


@Subject
class Descriptor(descriptors.Named):
    ValueType = Value
    on_get = Handler()
    on_set = Handler()
    on_del = Handler()
