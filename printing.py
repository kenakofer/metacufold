from colored import Fore, Back, Style
from datetime import datetime
from os import get_terminal_size
import sys
import platform
from metaculus import Metaculus
from manifold import Manifold
from arb import Order
import tabulate

from colorama import just_fix_windows_console
just_fix_windows_console()

CENT_SYMBOL="¢"
CLOCK_SYMBOL="⏰ "


def pretty_days(market):
    return str((market.close_time() - datetime.now()).days)

def pretty_percent(arb_market):
    string = ""
    if arb_market.order == Order.TOP:
        string += Fore.GREEN + Style.BOLD
    elif arb_market.order == Order.BOTTOM:
        string += Fore.RED + Style.BOLD
    prob = arb_market.probability()
    if prob < .02 or prob > .98:
        string += f'{round(prob*100, 2)}%'
    else:
        string += f'{round(prob*100)}%'

    if arb_market.order is not Order.MIDDLE:
        fee = arb_market.fee_adjustment()
        if fee != 0:
            string += f'{"+" if fee > 0 else ""}{round(fee*100)}{CENT_SYMBOL}'
        wiggle_adj = arb_market.wiggle_adjustment()
        if wiggle_adj != 0:
            string += f'{"+" if wiggle_adj > 0 else ""}{round(wiggle_adj*100)}w'

    string += Style.reset
    return string


def print_arb(arb):
    print()
    title_string = Style.BOLD + arb.title() + Style.reset + " (Arb score: " + str(int(arb.score())) + ")"
    line_len = min(get_terminal_size()[0], len(title_string))
    print("_" * line_len)
    print(title_string)
    print(arb._arb_score_breakdown)
    reversed_arb_markets = arb.arb_markets()[::-1]
    headers = ["%", CLOCK_SYMBOL, "Size", "Pos", "URL"]
    table = [[pretty_percent(am),
              pretty_days(am.market),
              am.market.size_string(),
              am.pretty_pos(),
              am.market.color(am.market.url())]
            for am in reversed_arb_markets]
    # print(tabulate.tabulate(table, headers=headers, tablefmt="fancy_grid"))
    print(tabulate.tabulate(table, headers=headers))
