import gunicorn.config
import os
import signal
import sys
import time
import threading


class ReloaderSetting(gunicorn.config.Setting):
    name = 'reloader'
    section = 'Greins'
    cli = ['--reloader']
    validator = gunicorn.config.validate_bool
    action = 'store_true'
    default = False
    desc = '''\
        Turn on automatic code reloading.

        This setting is intended for development.
        '''


class Reloader(threading.Thread):

    def __init__(self, extra_files=None, interval=1):
        super(Reloader, self).__init__()
        self.extra_files = set(extra_files or ())
        self.interval = interval

    def get_files(self):
        # Copyright notice.  This function is based on the autoreload.py from
        # the CherryPy trac which originated from WSGIKit which is now dead.
        def iter_module_files():
            for module in sys.modules.values():
                filename = getattr(module, '__file__', None)
                if filename:
                    old = None
                    while not os.path.isfile(filename):
                        old = filename
                        filename = os.path.dirname(filename)
                        if filename == old:
                            break
                    else:
                        if filename[-4:] in ('.pyc', '.pyo'):
                            filename = filename[:-1]
                        yield filename
        fnames = []
        fnames.extend(iter_module_files())
        fnames.extend(self.extra_files)
        return fnames

    def run(self):
        mtimes = {}
        while 1:
            for filename in self.get_files():
                try:
                    mtime = os.stat(filename).st_mtime
                except OSError:
                    continue
                old_time = mtimes.get(filename)
                if old_time is None:
                    mtimes[filename] = mtime
                    continue
                elif mtime > old_time:
                    print ' * Detected change in %r, reloading' % filename
                    os.kill(os.getpid(), signal.SIGQUIT)
            time.sleep(self.interval)


