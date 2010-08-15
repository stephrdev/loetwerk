# A global var. to remember autodiscover state.
LOADING = False

class StepAlreadyRegistered(Exception):
    pass

class StepNotFound(Exception):
    pass

class Registry(object):
    _registry = {}

    def add_step(self, name, func):
        # Check if the plugin is already registered.
        if func.__name__ in self._registry:
            raise StepAlreadyRegistered('The step %s has already \
                been registered.' % func.__name__)
        self._registry[func.__name__] = {'name': name, 'func': func}

    def list_steps(self):
        # Return a list of all plugins
        return self._registry

    def get_step(self, name):
        # We use this inner function to defer the Exception if a plugin
        # doesn't exist (we want to store this in the Build steps)
        def get_inner_step():
            # Get the plugin
            step = self._registry.get(name, {}).get('func', None)
            if not step:
                # No plugin found, raise an error.
                raise StepNotFound('Step %s not found.' % name)
            return step
        # Return the function.
        return get_inner_step

# Singleton instance of registry
registry = Registry()

def autodiscover():
    # Check if we already autodiscovering.
    global LOADING
    if LOADING:
        return
    LOADING = True

    # Late import some functions to do autodiscovery.
    import imp
    from django.utils.importlib import import_module
    from django.conf import settings

    # Check every installed app.
    for app in settings.INSTALLED_APPS:
        try:
            app_path = import_module(app).__path__
        except AttributeError:
            continue

        # We assume that plugins are stored in a build_steps module within
        # the app.
        try:
            imp.find_module('build_steps', app_path)
        except ImportError:
            continue

        # Load to build steps module to trigger the register call.
        import_module('%s.build_steps' % app)
    LOADING = False

# Just do the autodiscovery.
autodiscover()
