from werkzeug import Response, DispatcherMiddleware
from werkzeug.exceptions import NotFound

class Router(DispatcherMiddleware):
    def __init__(self, mounts={}):
        DispatcherMiddleware.__init__(self, self.not_found, mounts=mounts)

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

