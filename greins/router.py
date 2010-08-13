import logging
import string

from glob import glob
from os import getenv
from os.path import basename, join, splitext

from routes import Mapper
from routes.route import Route

CONF_D = getenv('GREINS_CONF_D') or "/etc/greins/conf.d"

class Router(object):
    def __init__(self):
        self.map = Mapper()
        self.defaults = {}
        self.logger = logging.getLogger('gunicorn')

        for cf in glob(join(CONF_D, '*.py')):
            cfname = splitext(basename(cf))[0]
            routes = []
            try:
                execfile(cf, {}, {'routes': routes})
            except:
                self.logger.exception("Exception loading config for %s" % cf)
                continue
            self.map.extend(
                (Route(None, r.get('path', ''), _app=r.get('app'),
                       **dict(self.defaults.items() +
                              r.get('kwargs', {}).items()))
                 for r in routes))
            self.logger.info("Loaded routes from %s" % cfname)
        self.logger.debug("Greins booted\n%s" % self)

    def __call__(self, environ, start_response):
        match = self.map.routematch(environ=environ)
        if not match:
            start_response('404 Not Found', {})
            return []
        return match[0]['_app'](environ, start_response)

    def __str__(self):
        #Technique taken from Routes mapper class
        table = [('Path', 'App', 'Options')] + \
                [(r.routepath,
                  "%s.%s" % (r._kargs['_app'].__module__,
                             r._kargs['_app'].__name__),
                  str([(k,v) for k,v in r._kargs.items() if k is not '_app']))
                 for r in self.map.matchlist]

        widths = [max(len(row[col]) for row in table)
                 for col in range(len(table[0]))]

        return '\n'.join(
            ' '.join(row[col].ljust(widths[col])
                     for col in range(len(widths)))
            for row in table)

router = Router()
