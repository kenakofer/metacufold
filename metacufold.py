#!/usr/bin/env python3
import sys
import os
from datetime import datetime
import argparse
from functools import reduce

from config import Config as C
from manifold import Manifold
from metaculus import Metaculus
from metaculus_bot_group import MetaculusBotGroup
from printing import print_arb


def sync():
    get_markets_sorted_by_difference()


def bet_once():
    print("bet_once...")
    print("API Key: " + C.API_KEY)

def help():
    print("help...")
    print("API Key: " + C.API_KEY)

def url_to_market(url):
    if "metaculus.com" in url:
        return Metaculus(url)
    elif "manifold.markets" in url:
        return Manifold(url)
    else:
        raise Exception("Unknown URL: " + url)


def arbs_from_file():
    # Read from additional_pairings.txt, ignoring # or blank lines, and split other lines into multiple urls by spaces
    additional_arbs = []
    with open("additional_arbs.txt", "r") as file:
        additional_arbs = [
            list(map(url_to_market, line.strip().split(" ")))
            for line in file.readlines() 
            if line.strip() != "" 
                and not line.strip().startswith("#")
        ]
    print("Adding " + str(len(additional_arbs)) + " arbs from additional_arbs.txt")
    return additional_arbs

def arb_score(markets):
    """
    Returns a score for a given arb, which is based on the difference in probabilities and the size of the markets.
    """
    
    # Sort the markets by probabilily
    markets.sort(key=lambda m: m.probability())

    # Size score is the product of the sizes of the markets, root the number of markets
    size_score = reduce(lambda x, y: x * y, [m.size() for m in markets], 1)
    size_score **= (1 / len(markets))

    bound = lambda x: min(max(x, 0.005), 0.995)

    lower = bound(markets[0].probability())
    upper = bound(markets[-1].probability())

    spread_score = (upper - lower)
    edginess_score = 1 / (upper * lower * (1 - upper) * (1 - lower))

    # Immanence score (if it closes sooner, it's better)
    immanence_score = 3600 * 24 * 365 / (markets[0].close_time() - datetime.now()).total_seconds()
    

    #print(size_score, spread_score, edginess_score, immanence_score)

    return size_score * spread_score**3 * edginess_score * immanence_score**.5



def get_markets_sorted_by_difference():
    market_pairs = MetaculusBotGroup.filtered_metaculus_arb_pairs()
    print(str(len(market_pairs)) + " valid market pairs found in Manifold's MetaculusBot group")
    market_pairs += arbs_from_file()

    # Sort markets by difference between manifold and metaculus probability
    market_pairs.sort(key=lambda pair: arb_score(pair), reverse=True)

    # Print out the top ten with their urls and probabilities
    for pair in market_pairs[:20]:
        print_arb(pair[0].title(), pair, arb_score(pair))

    return market_pairs


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
        elif sys.argv[1] == "bet-once":
            # Run the unfold method
            bet_once()
            sys.exit(0)
        elif sys.argv[1] == "help":
            # Print the help message
            help()
            sys.exit(0)
        else:
            print("Invalid argument: " + sys.argv[1])
            print()

    # If no valid arguments were given, print the help message
    help()
    sys.exit(1)
