from colored import Fore, Back, Style
import req as requests
from datetime import datetime
from prediction_site import PredictionSite
import re

from colorama import just_fix_windows_console
just_fix_windows_console()

class Metaculus(PredictionSite):
    def __init__(self, url):
        self._url = url
        self._market_id = str(re.search(r"questions/(\d+)", url).group(1))
        self._details = None

    def details(self):
        if not self._details:
            deets_url = "https://www.metaculus.com/api2/questions/" + self._market_id
            self._details = requests.get(deets_url).json()
            if not self._details or ('detail' in self._details and self._details['detail'] == "Not found."):
                print("Error: Could not get details for market " + self._market_id + " from " + deets_url)
                return None
        return self._details

    def title(self):
        return self.details()['title']

    def probability(self):
        full_community_prediction = self.details()["community_prediction"]["full"]

        if "q2" in full_community_prediction:
            return full_community_prediction["q2"]
        else:
            return None

    def size(self):
        return self.details()["number_of_forecasters"]

    def close_time(self):
        # Close time is for example "2031-01-01T00:00:00Z", convert to datetime
        return datetime.fromisoformat(self.details()["close_time"][:-1])

    def is_binary(self):
        deets = self.details()
        if "type" in deets["possibilities"]:
            return deets["possibilities"]["type"] == "binary"
        if "type" in deets:
            return deets["type"] == "group"

    def is_open(self):
        deets = self.details()
        # Check for "OPEN" active_state
        return "active_state" in deets and deets["active_state"] == "OPEN"

    def market_link(string):
        string = string.replace("/embed/", "/")
        # replace all // with / unless in https://
        string = re.sub(r"(?<!https:)//", "/", string)
        match = re.search(r"https://(www\.)?metaculus.com/questions/\d+", string)
        if not match:
            return None
        return str(match.group(0))

    def user_position_shares(self, force_refresh=False):
        # Not supported, default 0
        return 0


    def color(self, text):
        # Green back, black text
        return Back.GREEN + Fore.BLACK + text + Style.reset
