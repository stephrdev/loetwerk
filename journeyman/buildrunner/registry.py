LOADING = False

class StepAlreadyRegistered(Exception):
    pass

class StepNotFound(Exception):
    pass

class Registry(object):
    _registry = {}

    def add_step(self, name, func):
        if func.__name__ in self._registry:
            raise StepAlreadyRegistered('The step %s has already been registered.' % func.__name__)
        self._registry[func.__name__] = {'name': name, 'func': func}

    def list_steps(self):
        return self._registry

    def get_step(self, name):
        def get_inner_step():
            step = self._registry.get(name, {}).get('func', None)
            if not step:
                raise StepNotFound('Step %s not found.' % name)
            return step
        return get_inner_step

registry = Registry()

def autodiscover():
    global LOADING
    if LOADING:
        return
    LOADING = True

    import imp
    from django.utils.importlib import import_module
    from django.conf import settings

    for app in settings.INSTALLED_APPS:
        try:
            app_path = import_module(app).__path__
        except AttributeError:
            continue
        try:
            imp.find_module('build_steps', app_path)
        except ImportError:
            continue

        import_module("%s.build_steps" % app)
    LOADING = False

autodiscover()