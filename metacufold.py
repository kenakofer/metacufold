#!/usr/bin/env python3
import sys
import os
import argparse

from config import Config as C
from manifold import Manifold
from metaculus import Metaculus

def sync():
    get_markets_sorted_by_difference()


def bet_once():
    print("bet_once...")
    print("API Key: " + C.API_KEY)

def help():
    print("help...")
    print("API Key: " + C.API_KEY)


def get_markets_sorted_by_difference():
    markets = Manifold.fetch_filtered_metaculus_markets_json()
    # for market in markets:
        # print(market["question"] + " " + market["metaculus_link"])
    print(str(len(markets)) + " markets found")

    # Add metaculus probability to markets
    for market in markets:
        market.update({"metaculus_probability": Metaculus.fetch_market_probability(market["metaculus_id"])})
        market.update({"metaculus_predictions": Metaculus.fetch_market_size_indicator(market["metaculus_id"])})

    # Filter out markets that aren't binary on the Metaculus side
    markets = [market for market in markets if Metaculus.is_binary(market["metaculus_id"])]

    # Filter out markets that aren't open on the Metaculus side
    markets = [market for market in markets if Metaculus.is_open(market["metaculus_id"])]

    # Filter out markets with None metaculus probability
    markets = [market for market in markets if market["metaculus_probability"] is not None]

    # Sort markets by difference between manifold and metaculus probability
    markets.sort(key=lambda market: abs(market["probability"] - market["metaculus_probability"]), reverse=True)

    # Print out the top ten with their urls and probabilities
    for market in markets[:20]:
        print()
        print(market["question"])
        print( "  " + str(market['metaculus_probability']) + " (" + str(market['metaculus_predictions']) + ") " + market["metaculus_link"])
        print( "  " + str(market["probability"]) + " (" + str(market['totalLiquidity']) + ") " + str(market["url"]))


    return markets


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
