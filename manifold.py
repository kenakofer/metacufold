import req as requests
from time import time
import re

class Manifold:

    def __init__(self, url, market_id=""):
        self._url = url
        # https://manifold.markets/MetaculusBot/which-party-will-win-the-most-seats-152d40f3951e -> which-party-will-win-the-most-seats-152d40f3951e
        # Use regex to grab the string after the last slash (not slug)
        self._slug = str(re.search(r"/([^/]+)$", url).group(1))
        self._market_id = str(market_id)
        self._details = None
        self._summary = None

    def market_id(self):
        if not self._market_id:
            if not self._summary:
                self._summary = requests.get("https://manifold.markets/api/v0/slug/" + self._slug).json()
            self._market_id = str(self._summary['id'])
        return self._market_id

    def url(self):
        return self._url

    def details(self):
        if not self._details:
            self._details = requests.get("https://manifold.markets/api/v0/market/" + self.market_id()).json()
        return self._details

    def title(self):
        return self.details()['question']

    def probability(self):
        return round(self.details()['probability'], 2)

    def size(self):
        return self.details()['totalLiquidity']

    def is_binary(self):
        return self.details()["outcomeType"].startswith("BINARY")

    def is_open(self):
        return self.details()["closeTime"] > int(time()) * 1000

    def __str__(self):
        return self.title() + " (" + self.url() + ")"