import re
from functools import wraps


def _tag_cmd(func, pattern, event_type, respond=False):
    if not hasattr(func, '_command'):
        func._command = True
        func._event_type = event_type
        func._pattern = re.compile(pattern)
        if respond:
            func._respond = True
    return func


def listen_to(pattern='.*', event_type="message"):
    def decorator(func):
        return _tag_cmd(func, pattern, event_type)
    return decorator


def respond_to(pattern='.*', event_type="message"):
    def decorator(func):
        return _tag_cmd(func, pattern, event_type, respond=True)
    return decorator


def event_filter(*args, **kwargs):
    def decorator(func):
        func._eventfilter = True
        return func
    return decorator(*args, **kwargs)
