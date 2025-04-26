import time
from functools import wraps


def time_it(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f'Time taken by {func.__name__}: {end_time - start_time:.2f} seconds')
        return result

    return wrapper
