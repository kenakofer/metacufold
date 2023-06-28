#!/usr/bin/env python3
import sys
import os
import argparse

from config import Config as C
from manifold import Manifold
from metaculus import Metaculus
from metaculus_bot_group import MetaculusBotGroup

def sync():
    get_markets_sorted_by_difference()


def bet_once():
    print("bet_once...")
    print("API Key: " + C.API_KEY)

def help():
    print("help...")
    print("API Key: " + C.API_KEY)


def get_markets_sorted_by_difference():
    market_pairs = MetaculusBotGroup.filtered_metaculus_arb_pairs()
    print(str(len(market_pairs)) + " market pairs found in Manifold's MetaculusBot group")

    # Sort markets by difference between manifold and metaculus probability
    market_pairs.sort(key=lambda pair: abs(pair[0].probability() - pair[1].probability()), reverse=True)

    # Print out the top ten with their urls and probabilities
    for pair in market_pairs[:20]:
        print()
        print(pair[0].title())
        for m in pair:
            print( "  " + str(m.probability()) + " (" + str(m.size()) + ") " + m.url())


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
