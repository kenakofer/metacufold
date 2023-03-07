import req as requests
from time import time
import re

class Manifold:

    METACULUS_GROUP_MARKETS_URL = "https://manifold.markets/api/v0/group/by-id/5mFuwp5QX0sdZYdNq3Jx/markets"

    def fetch_metaculus_markets_json():
        """Get a list of all markets"""
        return requests.get(Manifold.METACULUS_GROUP_MARKETS_URL).json()


    def fetch_filtered_metaculus_markets_json():
        """Get a list of all markets"""
        markets = [
            market
            for market in Manifold.fetch_metaculus_markets_json()
            if market["isResolved"] == False
            and market["outcomeType"].startswith("BINARY")
            and market["closeTime"] > int(time()) * 1000
        ]

        # Overwrite the markets with the market details. Drop out a market if it doesn't have a Metaculus link
        for market in markets:
            market.update(Manifold.fetch_market_details(market["id"]))
            #Round
            market['probability'] = round(market['probability'], 2)
            market['totalLiquidity'] = round(market['totalLiquidity'])

        # Print markets without a metaculus link
        for market in markets:
            if market["metaculus_link"] is None:
                print("Market " + str(market["id"]) + " " + str(market['question']) + " has no Metaculus link")

        # Filter out markets that don't have a Metaculus link
        markets = [market for market in markets if market["metaculus_link"] is not None]

        # Get just the id from the metaculus link
        for market in markets:
            market["metaculus_id"] = re.search(r"questions/(\d+)", market["metaculus_link"]).group(1)

        return markets

    def fetch_market_details(market_id):
        """Get the description of a market"""
        response = requests.get("https://manifold.markets/api/v0/market/" + str(market_id)).json()

        # Search for a Metaculus link in the description
        metaculus_link = Manifold.search_for_metaculus_link(response["description"])
        # Remove "/embed/" from the link
        if metaculus_link is not None:
            metaculus_link = metaculus_link.replace("/embed/", "/")

        return {
            "id": market_id,
            "metaculus_link": metaculus_link,
            "probability": response["probability"],
            "totalLiquidity": response["totalLiquidity"],
        }


    # search recursively in 'description' for 'href': 'metaculus.com/questions/'
    # if found, return the 'href' value
    # if not found, return None
    def search_for_metaculus_link(description):
        if isinstance(description, dict):
            for key, value in description.items():
                if key == "href" and value.startswith("https://www.metaculus.com/questions/"):
                    return value
                elif key == "src" and value.startswith("https://www.metaculus.com/questions/"):
                    return value
                else:
                    r = Manifold.search_for_metaculus_link(value)
                    if r is not None:
                        return r
        elif isinstance(description, list):
            for item in description:
                r = Manifold.search_for_metaculus_link(item)
                if r is not None:
                    return r
        elif isinstance(description, str):
            # Regex simple string descriptions for the Metaculus link
            match = re.search(r"https://www.metaculus.com/questions/\d+", description)
            if match is not None:
                return match.group(0)
        return None