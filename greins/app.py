from glob import glob
from os.path import abspath, basename, isdir, join, splitext
from time import time

from gunicorn.app.wsgiapp import WSGIApplication
from gunicorn.config import Setting, validate_string

from greins.router import Router

def load_config(cf):
    """
    Read the configuration from a greins config file.
    Files should contain app handlers that define mount points for one or
    more wsgi applications. The handlers will be executed inside the environment
    returned created by the configuration file.
    """
    cfg = {
        "__builtins__": __builtins__,
        "__name__": "__config__",
        "__file__": abspath(cf),
        "__doc__": None,
        "__package__": None,
        "mounts": {}
    }
    execfile(cf, cfg, cfg)
    return cfg

class ConfigDir(Setting):
    name = "config_dir"
    section = "Config File"
    cli = ["-d", "--dir"]
    meta = "DIR"
    validator = validate_string
    default = "/etc/greins/conf.d"
    desc = """\
        The path to a Greins config directory.

        The directory will be scanned for .py files. Each file is evaluated for
        application-specific options. In addition to the Server Hooks allowed in
        a standard Gunicorn configuration file, each file may define a dict-like
        object called 'mounts' that maps uri paths to wsgi handlers.
        """

class GreinsApplication(WSGIApplication):

    def init(self, parser, opts, args):
        if not (opts.config_dir and isdir(opts.config_dir)):
            parser.error("config_dir must refer to an existing directory")

        self.mounts = {}
        self.hooks = {}
        #TODO: Server Hooks

    def load(self):
        for cf in glob(join(self.cfg.config_dir, '*.py')):
            cf_name = splitext(basename(cf))[0]
            try:
                cfg = load_config(cf)
            except:
                self.logger.exception("Exception reading config for %s" % cf_name)
            else:
                # Load all the mount points
                for r, a in cfg['mounts'].iteritems():
                    if r in self.mounts:
                        self.logger.warning("Duplicate routes for %s" % r)
                        continue
                    # Capture the handler in a closure
                    def wrap(app):
                        def app_with_env(env, start_response):
                            return app(env, start_response)
                        app_with_env.__name__ = app.__name__
                        return app_with_env
                    self.mounts[r] = wrap(a)
                self.logger.info("Loaded routes from %s" % cf_name)

        #Fold over all the config files and combine the mounts they load
        router = Router(mounts=self.mounts)
        self.logger.debug("Greins loaded\n%s" % router)
        return router

def run():
    """\
    The ``greins`` command line runner for launching Gunicorn with
    a greins configuration directory.
    """
    from greins.app import GreinsApplication
    GreinsApplication("%prog [OPTIONS]").run()
