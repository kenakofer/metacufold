# Import this file, then add a decorator like
#   @cache.memoize(expire=3600)
# to the function you want to cache.  The cache will be stored in selenium_cache.db

from diskcache import Cache
cache = Cache('cache/selenium')

def memoize(expire=3600):
    def outer_wrapper(func):
        def wrapper(*args, **kwargs):
            key = (func.__qualname__, args, kwargs)
            if key not in cache: 
                # print(f"Caching result for {key}")
                cache.set(key, func(*args, **kwargs), expire=expire)
            else:
                pass
                #print(f"Using cached result for {key}")
            return cache[key]
        return wrapper
    return outer_wrapper

def clear_cache():
    cache.clear()