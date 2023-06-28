import req as requests

class Metaculus:
    def fetch_market_details(market_id):
        url = "https://www.metaculus.com/api2/questions/" + str(market_id)
        print(url)
        return requests.get("https://www.metaculus.com/api2/questions/" + str(market_id)).json()


    def fetch_market_probability(market_id):
        full_community_prediction = Metaculus.fetch_market_details(market_id)["community_prediction"]["full"]

        if "q2" in full_community_prediction:
            return full_community_prediction["q2"]
        else:
            return None

    def fetch_market_size_indicator(market_id):
        details = Metaculus.fetch_market_details(market_id)
        print(details)
        return details["number_of_forecasters"]

    def is_binary(market_id):
        details = Metaculus.fetch_market_details(market_id)
        if "type" in details["possibilities"]:
            return Metaculus.fetch_market_details(market_id)["possibilities"]["type"] == "binary"
        if "type" in details:
            return details["type"] == "group"

    def is_open(market_id):
        details = Metaculus.fetch_market_details(market_id)
        # Check for "OPEN" active_state
        return "active_state" in details and details["active_state"] == "OPEN"
