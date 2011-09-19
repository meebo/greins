def synchronized(lock_attr):
    """Decorator for conveniently locking a member function
       with exception handling.  This could be replaced by 'with'
       in Python 2.5."""
    def decorator(function):
        def wrapped(self, *args, **kwargs):
            lock = getattr(self, lock_attr, None)
            lock.acquire()
            try:
                return function(self, *args, **kwargs)
            finally:
                lock.release()
        return wrapped
    return decorator
