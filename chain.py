class EventGet:
    def __init__(self, event_param):
        self.event_param = event_param


class EventSet:
    def __init__(self, event_param):
        self.event_param = event_param


class NullHandler:
    def __init__(self, successor=None):
        self._successor = successor

    def handle(self, obj, event):
        if self._successor is not None:
            return self._successor.handle(obj, event)


class IntHandler(NullHandler):
    def handle(self, obj, event):
        if isinstance(event, EventGet) and event.event_param is int:
            return obj.integer_field
        elif isinstance(event, EventSet) and type(event.event_param) is int:
            obj.integer_field = event.event_param
        else:
            return super().handle(obj, event)


class FloatHandler(NullHandler):
    def handle(self, obj, event):
        if isinstance(event, EventGet) and event.event_param is float:
            return obj.float_field
        elif isinstance(event, EventSet) and type(event.event_param) is float:
            obj.float_field = event.event_param
        else:
            return super().handle(obj, event)


class StrHandler(NullHandler):
    def handle(self, obj, event):
        if isinstance(event, EventGet) and event.event_param is str:
            return obj.string_field
        elif isinstance(event, EventSet) and type(event.event_param) is str:
            obj.string_field = event.event_param
        else:
            return super().handle(obj, event)