import req as requests

class Metaculus:
    def fetch_market_details(market_id):
        return requests.get("https://www.metaculus.com/api2/questions/" + str(market_id)).json()


    def fetch_market_probability(market_id):
        return Metaculus.fetch_market_details(market_id)["community_prediction"]["full"]["q2"]

    def fetch_market_prediction_count(market_id):
        return Metaculus.fetch_market_details(market_id)["number_of_predictions"]

    def is_binary(market_id):
        return Metaculus.fetch_market_details(market_id)["possibilities"]["type"] == "binary"
