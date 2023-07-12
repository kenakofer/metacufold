from colored import Fore, Back, Style
from datetime import datetime
from os import get_terminal_size
import sys
import platform
from metaculus import Metaculus
from manifold import Manifold
from arb import Order

from colorama import just_fix_windows_console
just_fix_windows_console()

UP_SYMBOL="▲"
DOWN_SYMBOL="▼"
CENT_SYMBOL="¢"

def pretty_pos(market):
    pos = round(market.user_position_shares())
    if pos == 0:
        return ""
    return UP_SYMBOL + str(pos) if pos > 0 else DOWN_SYMBOL + str(-pos)

def pretty_percent(arb_market):
    string = ""
    prob = arb_market.market.probability()
    if prob < .02 or prob > .98:
        string = f'{round(prob*100, 2)}%'
    else:
        string = f'{round(prob*100)}%'

    if arb_market.order is not Order.MIDDLE:
        fee = arb_market.fee_adjustment()
        if fee != 0:
            string += f'{"+" if fee > 0 else ""}{round(fee*100)}{CENT_SYMBOL}'
        wiggle_adj = arb_market.wiggle_adjustment()
        if wiggle_adj != 0:
            string += f'{"+" if wiggle_adj > 0 else ""}{round(wiggle_adj*100)}w'
    return string


def print_arb(arb):
    print()
    title_string = arb.markets()[0].title() + " (Arb score: " + str(int(arb.score())) + ")"
    line_len = min(get_terminal_size()[0], len(title_string))
    print("_" * line_len)
    print(title_string)
    print()
    for am in arb.arb_markets()[::-1]:
        print (" {:<0}{:<0}{:<6}{:<0}{:<10} {:<7}{:<10}{:<0}".format(
            Fore.GREEN + Style.BOLD if am.order == Order.TOP else "",
            Fore.RED + Style.BOLD if am.order == Order.BOTTOM else "",
            pretty_percent(am),
            Style.reset,
            "(" + str((am.market.close_time() - datetime.now()).days) + " days)",
            pretty_pos(am.market),
            am.market.color(am.market.url()),
            Style.reset))
