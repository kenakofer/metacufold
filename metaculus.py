from colored import Fore, Back, Style
import req as requests
from datetime import datetime
from prediction_site import PredictionSite
from config import Config as C
import re

from colorama import just_fix_windows_console
just_fix_windows_console()

class Metaculus(PredictionSite):

    PLATFORM_NAME = "Metaculus"

    def __init__(self, url):
        self._url = url
        self._market_id = str(re.search(r"questions/(\d+)", url).group(1))
        self._details = None
        self._user_position_shares = None

    def is_real_money(self):
        return False

    def details(self, invalidate_cache=False):
        if not self._details or invalidate_cache:
            deets_url = "https://www.metaculus.com/api2/questions/" + self._market_id
            self._details = requests.get(deets_url, invalidate_cache=invalidate_cache).json()
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

    def size_string(self):
        return "👥 " + str(self.size())

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

    def can_bet_down(self):
        return self.is_open()

    def market_link(string):
        string = string.replace("/embed/", "/")
        # replace all // with / unless in https://
        string = re.sub(r"(?<!https:)//", "/", string)
        match = re.search(r"https://(www\.)?metaculus.com/questions/\d+", string)
        if not match:
            return None
        return str(match.group(0))

    def user_position_shares(self, invalidate_cache=False, error_value=0):
        try:
            if not self._user_position_shares:
                url = 'https://www.metaculus.com/api2/predictions/?question=' + self._market_id + '&user=' + C.METACULUS_USER_ID
                authorization_header = "Token " + C.METACULUS_API_KEY
                headers = {'Authorization': authorization_header}
                response_json = requests.get(url, headers=headers).json()
                if len(response_json['results']) == 0 or len(response_json['results'][0]['predictions']) == 0:
                    self._user_position_shares = 0
                else:
                    my_prob = response_json['results'][0]['predictions'][-1]['x']
                    com_prob = self.probability()
                    # We don't have actual position shares, but if our probability is above
                    # the community's, we want that to be like a YES position. Subtract the
                    # two and adjust for edginess
                    difference = (my_prob - com_prob) * 100
                    edginess_factor = 1 / ((my_prob + .03) * (com_prob + .03) * (1.03 - my_prob) * (1.03 - com_prob))
                    self._user_position_shares = difference * edginess_factor
            return self._user_position_shares
        except Exception as e:
            print("Error getting user position shares for market " + self._market_id + " from Metaculus")
            print(e)
            return error_value

    def color(self, text):
        # Green back, black text
        return Back.GREEN + Fore.BLACK + text + Style.reset
