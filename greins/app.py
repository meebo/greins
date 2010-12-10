import glob
import inspect
import os.path

from gunicorn.app.wsgiapp import WSGIApplication
from gunicorn.config import make_settings

from greins.router import Router

hook_proxy_template = """\
def proxy%(spec)s:
    for handler in greins._hooks[name]['handlers']:
        handler%(spec)s
"""

class GreinsApplication(WSGIApplication):

    def init(self, parser, opts, args):
        if len(args) != 1:
            parser.error("No configuration directory specified.")
        if not os.path.isdir(args[0]):
            parser.error("APP_DIR must refer to an existing directory.")

        self.cfg.set("default_proc_name", parser.get_prog_name())
        self.app_dir = os.path.abspath(args[0])

        self._mounts = {}
        self._hooks = {}

        """
        Set up server hook proxies

        Rather than explicitly referring to defined Gunicorn server hooks,
        which may change in future versions of Gunicorn, take configuration
        settings from gunicorn.config.make_settings().

        For each setting in the "Server Hooks" category, create a proxy
        function (with matching arity in order to pass validation), which
        calls the hook for every loaded app that defines it.
        """
        for name, obj in make_settings().items():
            if obj.section == "Server Hooks":
                self._hooks[name] = {
                    "handlers": [],
                    "validator": obj.validator
                }
                # Grab the arg spec from the default handler
                spec = inspect.formatargspec(*inspect.getargspec(obj.default))
                # Make an environment to build and capture the proxy
                proxy_env = {
                    "greins": self,
                    "name": name
                }
                # Create the proxy
                exec hook_proxy_template % {'spec': spec} in proxy_env
                self.cfg.set(name, proxy_env['proxy'])

    def load(self):
        for cf in glob.glob(os.path.join(self.app_dir, '*.py')):
            cf_name = os.path.splitext(os.path.basename(cf))[0]
            cfg = {
                "__builtins__": __builtins__,
                "__name__": "__config__",
                "__file__": os.path.abspath(cf),
                "__doc__": None,
                "__package__": None,
                "mounts": {}
            }
            try:
                """
                Read ann app configuration from a greins config file.
                Files should contain app handlers with mount points
                for one or more wsgi applications.

                The handlers will be executed inside the environment
                created by the configuration file.
                """
                self.logger.info("Loading configuration for %s" % cf_name)
                execfile(cf, cfg, cfg)

                # Load all the mount points
                for r, a in cfg['mounts'].iteritems():
                    if r in self._mounts:
                        self.logger.warning("Duplicate routes for %s" % r)
                        continue
                    # Capture the handler in a closure
                    def wrap(app):
                        def app_with_env(env, start_response):
                            return app(env, start_response)
                        app_with_env.__name__ = app.__name__
                        return app_with_env
                    self._mounts[r] = wrap(a)

                # Set up server hooks
                for hook in self._hooks:
                    handler = cfg.get('%s' % hook)
                    if handler:
                        self._hooks[hook]['validator'](handler)
                        self._hooks[hook]['handlers'].append(handler)
            except:
                self.logger.exception("Exception reading config for %s:" % \
                                      cf_name)

        router = Router(mounts=self._mounts)
        self.logger.info("Greins booted successfully.")
        self.logger.debug("Routes:\n%s" % router)
        return router

    def _do_hook(self, name, argtuple):
        for handler in self._hooks[name]['handlers']:
            handler(*argtuple)

def run():
    """\
    The ``greins`` command line runner for launching Gunicorn with
    a greins configuration directory.
    """
    from greins.app import GreinsApplication
    GreinsApplication("%prog [OPTIONS] APP_DIR").run()
