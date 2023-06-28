import req as requests
import re

class Metaculus:
    def __init__(self, url):
        self._url = url
        self._market_id = str(re.search(r"questions/(\d+)", url).group(1))
        self._details = None

    def url(self):
        return self._url

    def market_id(self):
        return self._market_id

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

    def __str__(self):
        return self.title() + " (" + self.url() + ")"
