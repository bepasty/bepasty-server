import os

def errcheck(result, func, *arguments):
    if result < 0:
        try:
            mesg = os.strerror(-result)
        except ValueError:
            mesg = 'Unknown error'
        raise OSError(-result, mesg)

