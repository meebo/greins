from threading import RLock
from greins.synchronization import synchronized

# Based on werkzeug.DispatcherMiddleware
class Router(object):
    synchronize_mounts = synchronized('_mounts_lock')

    def __init__(self, mounts={}):
        self._mounts = mounts
        self._mounts_lock = RLock()

    @synchronize_mounts
    def add_mount(self, route, handler):
        return self._mounts.setdefault(route, handler)

    @synchronize_mounts
    def get_mount(self, script):
        return self._mounts.get(script)

    @synchronize_mounts
    def __str__(self):
        # Technique taken from Routes mapper class
        table = [('Path', 'App')] + \
                [(path, "%s.%s" % (app.__module__, app.__name__))
                 for path, app in self._mounts.items()]

        widths = [max(len(row[col]) for row in table)
                 for col in range(len(table[0]))]

        return '\n'.join(
            ' '.join(row[col].ljust(widths[col])
                     for col in range(len(widths)))
            for row in table)

    def __call__(self, environ, start_response):
        path_info = environ['PATH_INFO']
        script = path_info.rstrip('/')
        parts = path_info.split('/')
        while True:
            mount = self.get_mount(script)
            if mount is not None:
                environ['SCRIPT_NAME'] = script
                if script:
                    environ['PATH_INFO'] = path_info.split(script, 1)[1]
                return mount(environ, start_response)
            if script == '':
                 break
            parts.pop()
            script = '/'.join(parts)
        start_response('404 NOT FOUND', [])
        return "Not Found.\n"
