import os
import requests_cache

# Create the cache directory if it doesn't exist
if not os.path.exists("cache"):
    os.makedirs("cache")

# Create the cache

URLS_EXPIRE_AFTER = {
    'manifold.markets/api/v0/group/by-id/': 3600,
    'manifold.markets/api/v0/market/':      3 * 3600,
    'metaculus.com/api2/questions/':        3600,
    'manifold.markets/api/v0/slug/':        3600 * 24 * 365,   # One year, since the slug is only used to grab the id, and the id shouldn't change
    'futuur.com':                           3600,
    'api.futuur.com':                       3600,
}
session = requests_cache.CachedSession(
    'cache/requests_cache',
    backend='sqlite',
    expire_after=3600,
    urls_expire_after=URLS_EXPIRE_AFTER,
    stale_if_error=True
    )

def get(url, invalidate_cache=False, headers=None):
    # If invalidate_cache is true, clear the cache for this url
    if invalidate_cache:
        print(" xx Invalidating cache for " + url)
        session.cache.delete_url(url)
    r = session.get(url, headers=headers)
    return r

def clear_cache(platforms = None):
    if not platforms:
        # Clear the cache
        print("Clearing cache for all markets")
        # Get count of urls matching platform as we go
        count = 0
        for url in list(session.cache.urls)[:]:
            # Don't clear slugs, those shouldn't change
            if not "/slug/" in url:
                count += 1
                session.cache.delete_url(url)
        print("Cleared " + str(count) + " urls.")
    else:
        # Clear the cache for each platform
        for platform in platforms:
            print("Clearing cache for " + platform)
            # Get count of urls matching platform as we go
            count = 0
            for url in list(session.cache.urls)[:]:
                # Check for url in the domain name only. Don't clear slugs, those shouldn't change
                if platform in url.split("/")[2] and not "/slug/" in url:
                    count += 1
                    session.cache.delete_url(url)
            print("Cleared " + str(count) + " urls for " + platform)
