#!/usr/bin/env python3
import sys
import os
import yaml
from datetime import datetime
import argparse
from arb import Arb

from config import Config as C
from manifold import Manifold
from metaculus import Metaculus
from futuur import Futuur
from metaculus_bot_group import MetaculusBotGroup
from printing import print_arb
from req import clear_cache, get, session

def sync():
    get_arbs_sorted_by_score()


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
        return Manifold(url)
    elif "futuur.com" in url:
        return Futuur(url, yes_option=yes_option, no_option=no_option)
    else:
        raise Exception("Unknown URL: " + url)

def arbs_from_yaml():
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
        arbs = []
        for arb in yaml_contents:
            markets = []
            wiggles = []
            for market_info in arb:
                # Get the URL
                url = market_info["URL"]
                # Get the YES and NO options
                yes = market_info.get("YES_OPTION", None)
                no = market_info.get("NO_OPTION", None)
                wiggles.append(market_info.get("WIGGLE", 0))
                # Create the market
                market = url_to_market(url, yes_option=yes, no_option=no)
                market.probability()
                markets.append(market)
            arbs.append(Arb(markets, wiggles))
        return arbs




def get_arbs_sorted_by_score():
    arbs = MetaculusBotGroup.filtered_metaculus_arb_pairs()
    print(str(len(arbs)) + " valid market pairs found in Manifold's MetaculusBot group")
    arbs += arbs_from_yaml()

    # Sort markets by difference between manifold and metaculus probability
    arbs.sort(key=lambda arb: arb.score(), reverse=True)

    # Print out the top ten with their urls and probabilities
    for arb in arbs[:20]:
        print_arb(arb)

    return arbs


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
            # Run the fold method
            sync()
            sys.exit(0)
        elif sys.argv[1] == "clear-cache":
            clear_cache()
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
