import os
import requests_cache

# Create the cache directory if it doesn't exist
if not os.path.exists("cache"):
    os.makedirs("cache")

# Create the cache

URLS_EXPIRE_AFTER = {
    'manifold.markets/api/v0/group/by-id/': 3600,
    'manifold.markets/api/v0/market/':      3600,
}
session = requests_cache.CachedSession('cache/requests_cache', backend='sqlite', expire_after=3600, urls_expire_after=URLS_EXPIRE_AFTER)

def get(url, ignore_cache=False):
    r = session.get(url)
    return r

def clear_cache():
    # Clear the cache
    session.cache.clear()