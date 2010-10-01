import itertools
import logging
import string
import time

from glob import glob
from os import getenv
from os.path import basename, join, splitext

from werkzeug import Response, DispatcherMiddleware
from werkzeug.exceptions import NotFound

from collectd_aggregator_client import queue_data

CONF_D = getenv('GREINS_CONF_D') or "/etc/greins/conf.d"

class Router(DispatcherMiddleware):
    def __init__(self, mounts={}):
        self.logger = logging.getLogger('gunicorn')

        #Generate all mount tuples from a config file
        def load_mounts(mount_acc, cf):
            cfname = splitext(basename(cf))[0]
            cf_env = {'mounts': {}}
            try:
                execfile(cf, cf_env)
                for r, a in cf_env['mounts'].iteritems():
                    if r in mount_acc:
                        self.logger.warning("Duplicate route for %s" % r)
                    else:
                        def wrap(app):
                            def app_with_env(env, start_response):
                                def s_r(status, headers):
                                    code = status.split()[0]
                                    queue_data('greins',
                                               app.__name__,
                                               'status%s' % code,
                                               1,
                                               'sum')
                                    start_response(status, headers)
                                eval_env = {'app': app, 'env': env, 's_r': s_r}
                                start = time.time()
                                result = eval('app(env, s_r)', cf_env, eval_env)
                                resp_ms = (time.time() - start)*1000
                                queue_data('greins',
                                           app.__name__,
                                           'response_ms',
                                           resp_ms)
                                return result
                            app_with_env.__name__ = app.__name__
                            return app_with_env
                        mount_acc[r] = wrap(a)
            except:
                self.logger.exception("Exception loading config for %s" % cf)
                return
            self.logger.info("Loaded routes from %s" % cfname)
            return mount_acc

        #Chain together all the mounts from all configs
        mounts = reduce(load_mounts,
                        glob(join(CONF_D, '*.py')),
                        mounts)
        
        #Initialize the base class
        DispatcherMiddleware.__init__(self, self.not_found, mounts=mounts)
        self.logger.debug("Greins booted\n%s" % self)

    def __str__(self):
        #Technique taken from Routes mapper class
        table = [('Path', 'App')] + \
                [(path, "%s.%s" % (app.__module__, app.__name__))
                 for path, app in self.mounts.items()]

        widths = [max(len(row[col]) for row in table)
                 for col in range(len(table[0]))]

        return '\n'.join(
            ' '.join(row[col].ljust(widths[col])
                     for col in range(len(widths)))
            for row in table)

    def __call__(self, environ, start_response):
        response = DispatcherMiddleware.__call__(self, environ, start_response)
        return response

    def not_found(self, environ, start_response):
        return Response(status=404)(environ, start_response) 

router = Router()
