import inspect
import re

from . import metrics

class MetricsProvider:
    """ Autowiring dependency injection container for metrics """

    def __init__(self, observable, module=metrics):
        self._observable = observable
        self._module = module
        self._cache = {}

    def provide(self, name):
        if name in self._cache:
            return self._cache[name]

        klass = self.name_to_class(name)
        arg_names = self.init_arg_names(klass)
        args = [self.provide(i) for i in arg_names]

        instance = klass(*args)
        self._observable.add_listener(instance, instance.subscribe_to)
        self._cache[name] = instance

        return instance

    def name_to_class(self, name):
        class_name = name.title().replace('_', '')
        return getattr(self._module, class_name)

    def init_arg_names(self, klass):
        fun = getattr(klass, '__init__')
        argspec = inspect.getargspec(fun)
        return argspec.args[1:]
