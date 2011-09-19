def synchronized(lock_name):
    """Decorator for conveniently locking a member function
       with exception handling.  This could be replaced by 'with'
       in Python 2.5."""
    lock_attr = "_lock_" + lock_name
    def decorator(function):
        def wrapped(self, *args, **kwargs):
            lock = getattr(self, lock_attr, None)
            if lock is None:
                from threading import RLock
                lock = RLock()
                setattr(self, lock_attr, lock)
            lock.acquire()
            try:
                return function(self, *args, **kwargs)
            finally:
                lock.release()
        return wrapped
    return decorator
