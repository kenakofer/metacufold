import req as requests
from time import time
from manifold import Manifold
from metaculus import Metaculus
from arb import Arb
import re

class MetaculusBotGroup:

    METACULUS_GROUP_MARKETS_URL = "https://api.manifold.markets/v0/group/by-id/5mFuwp5QX0sdZYdNq3Jx/markets"

    def metaculus_group_market_summaries():
        """Get a list of all markets"""
        response = requests.get(MetaculusBotGroup.METACULUS_GROUP_MARKETS_URL)
        try:
            result = response.json()
            print("Found " + str(len(result)) + " markets in Metaculus group")
            return response.json()
        except:
            print("Error: Could not get markets from Metaculus group: " + MetaculusBotGroup.METACULUS_GROUP_MARKETS_URL)
            print(response)
            return []


    def get_ignore_markets_from_file():
        """Get a list of markets to ignore"""
        with open("ignore_markets.txt", "r") as file:
            return set([line.strip() for line in file.readlines() if not line.startswith("#")])


    def filtered_metaculus_arb_pairs(platforms  = None, status_callback = None):
        ignore_markets = MetaculusBotGroup.get_ignore_markets_from_file()

        # Filter to markets with lowercase class in platforms
        if platforms:
            if not "metaculus" in platforms or not "manifold" in platforms:
                print("Excluding MetaculusBotGroup, as it requires both metaculus and manifold platforms")
                return []

        """Get a list of all markets"""
        yield_count = 0
        summaries = MetaculusBotGroup.metaculus_group_market_summaries()
        for i, m in enumerate(summaries):
            if status_callback:
                status_callback("Getting Manifold's Metaculus group market statuses: " + str(i) + "/" + str(len(summaries)))
            if m["isResolved"] != False or not m["outcomeType"].startswith("BINARY") or m["closeTime"] < int(time()) * 1000 or m["url"] in ignore_markets:
                continue
            man_market = Manifold(m["url"], market_id = m["id"])

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

            if metaculus_link in ignore_markets:
                continue

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

            yield Arb([man_market, metaculus_market])
            yield_count += 1

        print("Yielded " + str(yield_count) + " suitable arbs from Metaculus group")
        return

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
