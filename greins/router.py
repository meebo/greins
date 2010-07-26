import logging

from glob import glob
from os import getenv
from os.path import join

from routes import Mapper
from routes.route import Route

CONF_D = getenv('GREINS_CONF_D') or "/etc/greins/conf.d"

class Router(object):
    def __init__(self):
        self.map = Mapper()
        self.defaults = {}

        for cf in glob(join(CONF_D, '*.py')):
            routes = []
            try:
                execfile(cf, {}, {'routes': routes})
            except:
                logging.exception("Exception loading config for %s" % cf)
                continue
            self.map.extend(
                (Route(name, url,
                       **dict(self.defaults.items() + kwargs.items()))
                 for name, url, kwargs in routes))

    def __call__(self, environ, start_response):
        match = self.map.routematch(environ=environ)
        if not match:
            start_response('404 Not Found', {})
            return []
        return match[0]['app'](environ, start_response)

router = Router()
