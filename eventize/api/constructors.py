# -*- coding: utf8 -*-
from . import Method, Attribute
from .tools import is_a_method
__all__ = ['handle', 'on_get', 'on_set', 'on_del', 'on_change', 'before', 'after']

def handle(obj, name, handler_type=None):
    if isinstance(obj, type):
        return _handle_cls(obj, name, handler_type)
    return _handle_obj(obj, name, handler_type)

def _handle_obj(obj, name, handler_type):
    cls = type(obj)
    cls_field = getattr(cls, name)
    if handler_type is None:
        handler_type = is_a_method(cls_field) and Method or Attribute
    if not isinstance(cls_field, handler_type):
        cls_field = handler_type(cls_field)
        setattr(cls, name, cls_field)

    return cls_field.get_value(obj)

def _handle_cls(cls, name, handler_type):
    cls_field = getattr(cls, name)
    if handler_type is None:
        handler_type = is_a_method(cls_field) and Method or Attribute
    if not isinstance(cls_field, handler_type):
        cls_field = handler_type(cls_field)
        setattr(cls, name, cls_field)
    return cls_field



def handler_with_event(event_name, handler_type=None):
    return lambda obj, name, handler=handler_type: getattr(handle(obj, name, handler), event_name)

on_get = handler_with_event('on_get', Attribute)
on_set = handler_with_event('on_set', Attribute)
on_del = handler_with_event('on_del', Attribute)
on_change = handler_with_event('on_change', Attribute)
before = handler_with_event('before', Method)
after  = handler_with_event('after', Method)
