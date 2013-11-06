# -*- coding: utf8 -*-
from .namedDescriptor import NamedDescriptor
from .events.event import AttributeEvent
from .events.handler import AttributeHandler, Handler

class Attribute(NamedDescriptor):
    on_get = AttributeHandler()
    on_set = AttributeHandler()
    on_del = AttributeHandler()

    def __init__(self, default=None):
        self.default = default

    def get(self, instance, name):
        self._assert_is_set(instance, name)
        event = self.on_get.call(instance, name=name)
        return event.returns()

    def set(self, instance, name, value):
        old_value = instance.__dict__.get(name, None)
        value = self.set_events(value, old_value)
        event = self.on_set.call(instance, name=name, value=value)
        instance.__dict__[event.name] = event.value

    def delete(self, instance, name):
        event = self.on_del.call(instance, name=name)
        del instance.__dict__[event.name]

    def _assert_is_set(self, instance, name):
        if not self.is_set(instance, name):
            if self.default is None:
                raise AttributeError("'%s' has no attribute '%s'" % (instance, name))
            self.set(instance, name, self.default)

    def set_events(self, subject, copy_from=None):
        on_get = getattr(copy_from, 'on_get', Handler())
        on_set = getattr(copy_from, 'on_set', Handler())
        on_del = getattr(copy_from, 'on_del', Handler())
        on_get.event_class = AttributeEvent
        on_set.event_class = AttributeEvent
        on_del.event_class = AttributeEvent

        try:
            setattr(subject, 'on_get', on_get)
            setattr(subject, 'on_set', on_set)
            setattr(subject, 'on_del', on_del)
        except AttributeError:
            subject = self.subtype_subject(subject, on_get=on_get, on_set=on_set, on_del=on_del)
        return subject

    def subtype_subject(self, subject, **handlers):
        subject_type = type(subject)
        bases = (subject_type, ) + subject_type.__bases__
        attrs = dict(subject_type.__dict__)
        try:
            subject = type(subject_type.__name__, bases, attrs)(subject)
            for handler_name, handler in handlers.items():
                setattr(subject, handler_name, handler)
            return subject
        except TypeError:
            return subject
