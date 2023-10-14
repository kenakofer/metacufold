#!/usr/bin/env python3
import sys
import os
import yaml
import argparse
from arb import Arb

from config import Config as C
from manifold import Manifold
from metaculus import Metaculus
from futuur import Futuur
from predictit import Predictit
from metaculus_bot_group import MetaculusBotGroup
from printing import print_arb
from req import clear_cache, get
from selenium_cache import clear_cache as clear_selenium_cache
import itertools

def sync(platforms):
    get_arbs_sorted_by_score(platforms)


def bet_once():
    print("bet_once...")
    print("API Key: " + C.API_KEY)

def help():
    print("help...")
    print("API Key: " + C.API_KEY)

def url_to_market(url, yes_option=None, no_option=None):
    if "metaculus.com" in url:
        return Metaculus(url)
    elif "manifold.markets" in url:
        return Manifold(url, yes_option=yes_option, no_option=no_option)
    elif "futuur.com" in url:
        return Futuur(url, yes_option=yes_option, no_option=no_option)
    elif "predictit.org" in url:
        return Predictit(url, yes_option=yes_option, no_option=no_option)

    else:
        raise Exception("Unknown URL: " + url)

def arbs_from_yaml(platforms = None, status_callback = None):
    """ Example entry in the list, note the optional YES/NO under each URL:
    - - URL: https://manifold.markets/ACXBot/9-will-a-nuclear-weapon-be-used-in
    - URL: https://www.metaculus.com/questions/13933/10-deaths-from-nuclear-detonation-in-2023/
    - URL: https://futuur.com/q/115818/will-there-be-a-nuclear-conflict-in-the-world-by-the-end-of-2023
      YES_OPTION: "Yes, In 2022 Or 2023"
      NO_OPTION: "No, Not Before 2024"
      """
    import yaml
    with open("additional_arbs.yaml", "r") as file:
        yaml_contents = yaml.load(file, Loader=yaml.FullLoader)
        # Create arbs, each arb having a list of markets
        for i, arb in enumerate(yaml_contents):
            markets = []
            wiggles = []
            inverts = []
            boost = 0
            title = None
            if status_callback:
                status_callback("Getting arbs from yaml: " + str(i+1) + "/" + str(len(yaml_contents)))
            for market_info in arb:
                # Get the URL
                if "BOOST" in market_info:
                    boost = market_info["BOOST"]
                    continue
                if "TITLE" in market_info:
                    title = market_info["TITLE"]
                    continue
                url = market_info["URL"]
                if not url:
                    print("No URL found in market_info: " + str(market_info))
                # Get the YES and NO options
                yes = market_info.get("YES_OPTION", None)
                no = market_info.get("NO_OPTION", None)
                wiggle = market_info.get("WIGGLE", 0)
                invert = market_info.get("INVERT", False)
                # Create the market
                market = url_to_market(url, yes_option=yes, no_option=no)
                # Exclude market if not in platforms
                if platforms and market.PLATFORM_NAME.lower() not in platforms:
                    continue
                # Ensure now that we can actually get the probability
                market.probability()
                markets.append(market)
                wiggles.append(wiggle)
                inverts.append(invert)
            yield Arb(markets, wiggle_factors=wiggles, boost=boost, inverts=inverts, title=title)
        return


def get_arbs_sorted_by_score(platforms, status_callback=None):
    arbs = list(get_arbs_generator(platforms, status_callback=status_callback))
    if status_callback:
        status_callback("Sorting " + str(len(arbs)) + " arbs by score")

    # Sort markets by difference between manifold and metaculus probability
    arbs.sort(key=lambda arb: arb.score(), reverse=True)

    # Print out the top arbs with their urls and probabilities
    for i, arb in enumerate(arbs[:20]):
        if status_callback:
            status_callback("Printing arb " + str(i+1) + " of top 20 to console")
        if (arb.score() <= 0):
            break
        print_arb(arb)

def get_arbs_generator(platforms, status_callback=None):
    yaml_arbs = arbs_from_yaml(platforms, status_callback=status_callback)
    met_bot_arbs = MetaculusBotGroup.filtered_metaculus_arb_pairs(platforms, status_callback=status_callback)

    for a in itertools.chain(yaml_arbs, met_bot_arbs):
        # Filter to markets with lowercase class in platforms
        if platforms:
            for am in a.arb_markets():
                if am.market.PLATFORM_NAME.lower() not in platforms:
                    a.remove_market(am)

        yield a


# For the main method, check arguments to see function to run
if __name__ == "__main__":

    # Create the cache directory if it doesn't exist
    if not os.path.exists("cache"):
        os.makedirs("cache")

    # Create the logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Check the first argument
    if len(sys.argv) > 1:
        # Check the first argument
        if sys.argv[1] == "sync":
            # Run the sync method, passing in any addiotanl arguments
            sync(sys.argv[2:])
            sys.exit(0)
        elif sys.argv[1] == "clear-cache":
            clear_cache(sys.argv[2:])
            if (sys.argv[2:] and "selenium" in sys.argv[2:]):
                clear_selenium_cache()
                print("Selenium cache cleared")
            print("Cache cleared")
            sys.exit(0)
        elif sys.argv[1] == "bet-once":
            # Run the unfold method
            bet_once()
            sys.exit(0)
        elif sys.argv[1] == "help":
            # Print the help message
            help()
            sys.exit(0)
        elif sys.argv[1] == "test-cache":
            for i in range(10):
                print("Test " + str(i+1) + ":")
                get("https://www.metaculus.com/questions/13933")
            sys.exit(0)
        else:
            print("Invalid argument: " + sys.argv[1])
            print()

    # If no valid arguments were given, print the help message
    help()
    sys.exit(1)
