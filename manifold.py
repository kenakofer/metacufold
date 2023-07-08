import req as requests
from prediction_site import PredictionSite
from time import time
from datetime import datetime
import re

class Manifold(PredictionSite):

    def __init__(self, url, market_id=""):
        self._url = url
        # https://manifold.markets/MetaculusBot/which-party-will-win-the-most-seats-152d40f3951e -> which-party-will-win-the-most-seats-152d40f3951e
        # Use regex to grab the string after the last slash (not slug)
        self._slug = str(re.search(r"/([^/]+)$", url).group(1))
        self._market_id = str(market_id)
        self._details = None
        self._all_positions = None
        self._summary = None

    def market_id(self):
        if not self._market_id:
            if not self._summary:
                self._summary = requests.get("https://manifold.markets/api/v0/slug/" + self._slug).json()
            self._market_id = str(self._summary['id'])
        return self._market_id

    def details(self):
        if not self._details:
            self._details = requests.get("https://manifold.markets/api/v0/market/" + self.market_id()).json()
        return self._details

    def user_position_shares(self, username, force_refresh=False):
        if not self._all_positions or force_refresh:
            self._all_positions = requests.get("https://manifold.markets/api/v0/market/" + self.market_id() + "/positions", invalidate_cache=force_refresh).json()
            if not self._all_positions:
                print("Error: Could not get position for market " + self.market_id())
                return 0
        for position in self._all_positions:
            if position['userName'] == username:
                totalShares = 0
                if 'YES' in position['totalShares']:
                    totalShares += position['totalShares']['YES']
                if 'NO' in position['totalShares']:
                    totalShares -= position['totalShares']['NO']
                return totalShares
        return 0

    def title(self):
        return self.details()['question']

    def probability(self):
        return round(self.details()['probability'], 2)

    def size(self):
        return self.details()['totalLiquidity']

    def close_time(self):
        # Close time is in milliseconds since the epoch, convert to datetime
        return datetime.fromtimestamp(self.details()["closeTime"] / 1000)

    def is_binary(self):
        return self.details()["outcomeType"].startswith("BINARY")

    def is_open(self):
        return self.details()["closeTime"] > int(time()) * 1000