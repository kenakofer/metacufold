from colored import Fore, Back, Style
import req as requests
from datetime import datetime, timedelta
from string import Template
from prediction_site import PredictionSite
import json
import re

"""
- 10% fee on profits every time a market resolves (very bad)
- 5% fee on ALL withdrawls from PI, including principal (very bad)
- 1099-MISC provided by PI calculates income as profits minus their 10% fee
  on profits and minus their 5% fee to withdraw the profits, but DOES NOT
  subtract out the 5% for principal withdrawn.

For example:
- Start with $90 in your bank account
- Put it into PI
- Bet it all on 100 shares costing .90 each
- Win, with a profit of $10, before PI's cut
    - PI taken 10% or $1, leaving you with $9 profit on the platform.
- Your balance on PI now reads $99
- You withdraw everything, and PI takes 5%, about $5 in fees
- You have $94 in your bank account, a profit of 4.4%

Later on...
- Your 1099 will show an income of $10 - $1 - $0.50 = $8.50, because only the
fees on profits are subtracted. The 5% * $90 = 4.50 in principal withdrawl fees
is not subtracted, and if taxed at 25%, that false income will cost you another
$1.125 on tax day.
- The extra tax burden is close to principal * 5% * 25% == principal * 1.25%
- You can think of this as incurring a debt of 1.25% of any deposit, to be paid
  off after taxes after withdrawl of the principal. An easier way to think of it
  is as a higher withdrawl percentage of 6.25%, on the principal

Another example:
- Start with $100 in your bank account
- Put it into PI
- Bet it all on 1000 shares costing .10 each
- Win, with a profit of $900, before PI's cut
    - PI taken 10% or $90, leaving you with $810 profit on the platform.
- Your balance on PI now reads $910
- You withdraw everything, PI takes 5% = $45.5 in fees
- You have $864.5 in your bank account, a profit of 764.5%.

The effect of multiple bets:
- The winnings cut takes from the profits of every victory, but only cuts into
  the profit portion. Losses on other bets do not offset.
- The withdrawl cut is minimized if you use the deposit in PI for many bets
  in sequence. In other words, you may only need to make one large deposit for a
  lifetime of investments on the platform, especially if you can get it to grow.
- Additionally, lost bets offset the withdrawl cut
- Ditto for the extra tax burden, just minimize deposits.
- For the bulk of the 1099 tax burden, wins on PI will count against
  losses, so it's a tax on PI's net gains. However, wins/losses on
  PI can't be reported against wins/losses on other platforms.

((start / chance - start) * win_cut + start) * withdraw_cut - start

Let a Fee Adjusted Share Price (FASP) be the amount needed to deposit into the
market, purchase 1 Fee Adjusted Share (FAS), and, conditional on winning, obtain
1 dollar out.

Conservatively:
For PI, 1 share = .85 FAS
        1.176 shares = 1 FAS

Less conservatively, but still reasonable with many bets over a period of time:
For PI, 1 share = .875 FAS
        1.14 shares = 1 FAS

For a numbers sanity check, read https://www.lesswrong.com/posts/c3iQryHA4tnAvPZEv/limits-of-current-us-prediction-markets-predictit-case-study

"""

# .1 at least, make more conservative for the other fees
WINNINGS_CUT_FACTOR = .15


class Predictit(PredictionSite):

    PLATFORM_NAME="PredictIt"
    API_TEMPLATE=Template('https://www.predictit.org/api/marketdata/markets/$id')
    RELATED_TEMPLATE=Template('https://www.predictit.org/api/Market/$id/related')
    BROWSER_TEMPLATE=Template('https://www.predictit.org/markets/detail/$id')

    def __init__(self, url, yes_option=None, no_option=None):
        yes_option = yes_option or "YES"
        no_option = no_option or "NO"
        self._url = url
        # Example url: https://www.predictit.org/markets/detail/7053/Who-will-win-the-2024-Republican-presidential-nomination
        # Use regex to grab the number after the detail/ and before the /
        self._market_id = str(re.search(r"detail/([^/]+)", url).group(1))
        self._details = None
        self._yes_option = yes_option
        self._no_option = no_option
        self._total_shares_traded = None

    def details(self):
        if not self._details:
            details_url = Predictit.API_TEMPLATE.substitute(id=self.market_id())
            self._details = requests.get(details_url).json()
        return self._details

    def title(self):
        return self.details()['name']

    def probability(self):
        yes_option = self._get_yes_option()
        assert yes_option, "Error: Could not find yes option (" + self._yes_option + ") in Predictit market: " + self._url
        return yes_option['bestBuyYesCost']

    def fee_adjustment(self, buying_yes):
        prob = self.probability()
        inversion = 1
        if not buying_yes:
            prob = 1 - prob
            inversion = -1
        return inversion * WINNINGS_CUT_FACTOR * (1-prob)

    def size(self):
        if self._total_shares_traded == None:
            market_json = self._search_recursive_related_for_self()
            if market_json:
                self._total_shares_traded = market_json['totalSharesTraded']
            else:
                print("Couldn't find it")
        return int(self._total_shares_traded / 1000) or 1

    def size_string(self):
        TRADES_SYMBOL = '💱 '
        return TRADES_SYMBOL + str(self.size()) + 'k'

    def _search_recursive_related_for_self(self, starting_id=None, depth_remaining=2):
        # Recursively fetch related markets, until we find the entry for this market
        # If we don't find it, return None
        if depth_remaining == 0:
            return None
        if not starting_id:
            starting_id = self.market_id()
        related_url = Predictit.RELATED_TEMPLATE.substitute(id=starting_id)
        related_json = requests.get(related_url).json()
        for market_json in related_json:
            # print("Checking market: " + str(market_json['marketId']) + " against " + str(self.market_id()) + " with depth " + str(depth_remaining))
            if str(market_json['marketId']) == str(self.market_id()):
                return market_json
            else:
                recursive_result = self._search_recursive_related_for_self(starting_id=market_json['marketId'], depth_remaining=depth_remaining-1)
                if recursive_result:
                    return recursive_result
        return None

    def close_time(self):
        # Close time is for example "2031-01-01T00:00:00Z", convert to datetime
        # return datetime.fromisoformat(self.details()["bet_end_date"][:-1])
        # Just return a date time 1 year from now
        return datetime.now() + timedelta(days=365)

    def is_binary(self):
        return self._get_yes_option() 

    def is_open(self):
        deets = self.details()
        return deets['status'] == "Open"

    def _get_yes_option(self):
        if not 'contracts' in self.details():
            print("Error: Could not find contracts in Predictit market: " + self._url)
            print("details: " + str(self.details()))
        for outcome in self.details()['contracts']:
            # Compare case insesitive
            if not 'name' in outcome:
                print("Error: Could not find name in outcome: " + str(outcome))
            if outcome['name'].lower() == self._yes_option.lower():
                return outcome
        print("Error: Could not find yes option (" + self._yes_option + ") in Predictit market: " + self._url)
        print("Contracts: " + str(self.details()['contracts']))
        return None

    def color(self, text):
        return Fore.BLUE + Style.BOLD + text + Style.reset
