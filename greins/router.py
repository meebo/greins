import logging

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
            namespace = '/' + splitext(basename(cf))[0]
            routes = []
            try:
                execfile(cf, {}, {'routes': routes})
            except:
                self.logger.exception("Exception loading config for %s" % cf)
                continue
            self.map.extend(
                (Route(None, url,
                       **dict(self.defaults.items() + kwargs.items()))
                 for url, kwargs in routes), namespace)
            self.logger.info("Loaded routes from %s" % namespace[1:])

    def __call__(self, environ, start_response):
        match = self.map.routematch(environ=environ)
        if not match:
            start_response('404 Not Found', {})
            return []
        return match[0]['app'](environ, start_response)

router = Router()
