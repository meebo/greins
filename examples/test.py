# -*- coding: utf-8 -
#
# This file is part of greins released under the MIT license. 
# See the NOTICE for more information.
#
# Example code from Eventlet sources

def pre_request(worker, req):
    worker.log.info('Request: %s %s', req.method, req.path)

def create_app(*body_parts):
    def app(environ, start_response):
        status = '200 OK'
        response_headers = [
            ('Content-type','text/plain')
        ]
        start_response('200 OK', response_headers)
        return iter(body_parts)
    return app

mounts = {
    '/hello': create_app('Hello, World!\n'),
    '/goodbye': create_app('Goodbye, cruel World!\n'),
    '/multi': create_app('Two ', 'Chunks', '\n')
}
