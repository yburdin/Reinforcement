import time


class Decorators:
    @staticmethod
    def timed(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            return_value = func(*args, **kwargs)
            end = time.time()
            if end - start > 0.1:
                print(f'{func.__name__} time {(end - start):.3g} seconds')
            return return_value

        return wrapper
