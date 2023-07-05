
from functools import partial

class MetaSingleton(type):
    _instances={}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton,cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class State(metaclass=MetaSingleton):
    def use(self, key, init_value=None):
        if "state" not in self.__dict__.keys():
            self.state = {}
        self.state[key] = {"value":init_value, "updateMethods":{}}

    def set(self, key, value):
        self.state[key]["value"] = value
        for method in self.state[key]["updateMethods"].values():
            method(value)

    def bind(self, key, id, method):
        self.state[key]["updateMethods"][id] = method
        method(self.value(key))

    def value(self, key):
        return self.state[key]["value"] 
       
def setStateFunc(key):
    return partial(State().set, key)