from threading import Thread


def threaded(func):
    """
    decorator to run a function asynchronously (in a thread)

    be careful: do not access flask threadlocals in f!
    """
    def wrapper(*args, **kwargs):
        t = Thread(target=func, args=args, kwargs=kwargs)
        t.start()
    return wrapper
