from datetime import datetime
from os import get_terminal_size
import sys
import platform
from metaculus import Metaculus
from manifold import Manifold

HEADER = '\033[95m'
OKBLUE = '\033[94m'
GREEN = '\033[32m'
WHITE = '\033[37m'
BLACK = '\033[30m'
RED = '\033[31m'
OKCYAN = '\033[96m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
GREEN_BACK = '\033[42m'
BLUE_BACK = '\033[44m'

if hasattr(sys.stderr, "isatty") and sys.stderr.isatty():
    if platform.system() == "Windows":
        ## Delete all colors
        HEADER = ''
        OKBLUE = ''
        GREEN = ''
        WHITE = ''
        BLACK = ''
        RED = ''
        OKCYAN = ''
        OKGREEN = ''
        WARNING = ''
        FAIL = ''
        ENDC = ''
        BOLD = ''
        UNDERLINE = ''
        GREEN_BACK = ''
        BLUE_BACK = ''


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
        print (" {:<0}{:<0}{:<4}{:<0} {:<10} {:<0}{:<0}{:<10}{:<0}".format(
            BOLD + GREEN if m is sorted_arb[0] else "",
            BOLD + RED if m is sorted_arb[-1] else "",
            pretty_percent(m.probability()),
            ENDC,
            "(" + str((m.close_time() - datetime.now()).days) + " days)",
            GREEN_BACK + BLACK if isinstance(m, Metaculus) else "",
            BLUE_BACK + WHITE if isinstance(m, Manifold) else "",
            m.url(),
            ENDC))


