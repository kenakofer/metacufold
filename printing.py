from colored import Fore, Back, Style
from datetime import datetime
from os import get_terminal_size
import sys
import platform
from metaculus import Metaculus
from manifold import Manifold

def pretty_percent(prob):
    if prob < .02 or prob > .98:
        return f'{round(prob*100, 2)}%'
    else:
        return f'{round(prob*100)}%'

def print_arb(title, arb, arb_score):
    print()
    title_string = title + " (Arb score: " + str(int(arb_score)) + ")"
    line_len = min(get_terminal_size()[0], len(title_string))
    print("_" * line_len)
    print(title_string)
    print()
    sorted_arb = sorted(arb, key=lambda m: m.probability(), reverse=True)
    for m in sorted_arb:
        print (" {:<0}{:<0}{:<4}{:<0} {:<10} {:<11}{:<10}{:<0}".format(
            Fore.GREEN + Style.BOLD if m is sorted_arb[0] else "",
            Fore.RED + Style.BOLD if m is sorted_arb[-1] else "",
            pretty_percent(m.probability()),
            Style.reset,
            "(" + str((m.close_time() - datetime.now()).days) + " days)",
            "Pos: " + str(int(m.user_position_shares()))+ " " if m.user_position_shares() != 0 else "",
            m.color(m.url()),
            Style.reset))
