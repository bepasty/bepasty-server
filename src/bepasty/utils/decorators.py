from threading import Thread


def threaded(func):
    """
    Decorator to run a function asynchronously (in a thread).

    Be careful: do not access Flask thread-locals in func!
    """
    def wrapper(*args, **kwargs):
        t = Thread(target=func, args=args, kwargs=kwargs)
        t.start()
    return wrapper
