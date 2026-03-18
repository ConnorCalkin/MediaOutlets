import logging


def debug_generator(func):
    '''A decorator that logs the function name and its arguments each time the generator is called.'''
    def wrapper(*args, **kwargs):
        logging.debug(
            f"Calling function: {func.__name__} with args: {args} and kwargs: {kwargs}")
        return func(*args, **kwargs)
    return wrapper
