import req as requests
from time import time
from manifold import Manifold
from metaculus import Metaculus
from arb import Arb
import re

class MetaculusBotGroup:

    METACULUS_GROUP_MARKETS_URL = "https://manifold.markets/api/v0/group/by-id/5mFuwp5QX0sdZYdNq3Jx/markets"

    def metaculus_group_market_summaries():
        """Get a list of all markets"""
        return requests.get(MetaculusBotGroup.METACULUS_GROUP_MARKETS_URL).json()


    def get_ignore_markets_from_file():
        """Get a list of markets to ignore"""
        with open("ignore_markets.txt", "r") as file:
            return [line.strip() for line in file.readlines()]


    def filtered_metaculus_arb_pairs(platforms  = None):
        ignore_markets = MetaculusBotGroup.get_ignore_markets_from_file()

        # Filter to markets with lowercase class in platforms
        if platforms:
            if not "metaculus" in platforms or not "manifold" in platforms:
                print("Excluding MetaculusBotGroup, as it requires both metaculus and manifold platforms")
                return []

        """Get a list of all markets"""
        manifold_markets = [
            Manifold(m["url"], market_id = m["id"])
            for m in MetaculusBotGroup.metaculus_group_market_summaries()
            if m["isResolved"] == False
            and m["outcomeType"].startswith("BINARY")
            and m["closeTime"] > int(time()) * 1000
            and m["url"] not in ignore_markets
        ]

        arbs = []

        for man_market in manifold_markets:
            # Search for a Metaculus link in the description
            metaculus_link = MetaculusBotGroup.search_for_metaculus_link(man_market.details()["description"])

            if metaculus_link is None:
                # Print and skip markets without a metaculus link
                print("Market has no Metaculus link: " + str(man_market))
                print(man_market.details()["description"])
                continue

            # print(man_market.url())

            metaculus_link = metaculus_link.replace("/embed/", "/")
            metaculus_link = metaculus_link.replace("www.", "")

            metaculus_market = Metaculus(metaculus_link)

            if (metaculus_market.details() is None):
                print("  Could not fetch details for " + str(metaculus_link))
                print("  Coming from manifold: " + str(man_market))
                continue

            # Filter out markets that aren't binary on the Metaculus side
            if (metaculus_market.is_binary() == False):
                print("Market is not binary: " + str(metaculus_market))
                continue

            # Filter out markets that aren't open on the Metaculus side
            if (metaculus_market.is_open() == False):
                print("Market is not open: " + str(metaculus_market))
                continue

            # Filter out markets with None metaculus probability
            if (metaculus_market.probability() == None):
                print("Market has no probability: " + str(metaculus_market))
                continue

            arbs.append(Arb([man_market, metaculus_market]))

        return arbs

    # search recursively in 'description' for 'href': 'metaculus.com/questions/'
    # if found, return the 'href' value
    # if not found, return None
    def search_for_metaculus_link(description):
        if isinstance(description, dict):
            for key, value in description.items():
                if key == "href" and Metaculus.market_link(value):
                    return Metaculus.market_link(value)
                elif key == "src" and Metaculus.market_link(value):
                    return Metaculus.market_link(value)
                else:
                    r = MetaculusBotGroup.search_for_metaculus_link(value)
                    if r is not None:
                        return r
        elif isinstance(description, list):
            for item in description:
                r = MetaculusBotGroup.search_for_metaculus_link(item)
                if r is not None:
                    return r
        elif isinstance(description, str):
            if Metaculus.market_link(description):
                return Metaculus.market_link(description)
        return None
