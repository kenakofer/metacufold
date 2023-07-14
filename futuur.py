from colored import Fore, Back, Style
import req as requests
from datetime import datetime
from string import Template
from prediction_site import PredictionSite
import json
import re

from colorama import just_fix_windows_console
just_fix_windows_console()

"""
Withdrawl fee is .004 ETH which is ~$5.41
Long enough on the platform and this should become insubstantial.

On the well established Brazil 2022, with $21k of "volume", Lula and Bolsonaro
go head to head, but shares cost 68 and 40 cents respectively. My existing lula
shares sell at 61.5 cents. So just to buy and sell a small amount would lose 5.5
percent

I can't find any other substantial fees, but because of the risks or unknown
fees of dealing in unfamiliar crypto and legal territory, I'll say
1 share = .9 fee adjusted shares

From the FAQ: https://docs.futuur.com/faqs

Futuur uses the LS-LMSR (Liquidity-Sensitive Logarithmic Scoring Rule) market
maker, an approach that builds on the foundation of the original LMSR algorithm,
widely used in prediction market applications.

If your cumulative lifetime deposits exceed $2000 USD equivalent, Futuur will
require this as part of its legally mandated KYC requirements.  Hey, we don’t
make the rules!

Independent of the currency used, all real-money currencies are combined in the
same liquidity pool. So if you are betting in BTC and someone else bets USDC in
the same market, both bets will impact the prices and increase overall liquidity
in the market.


"""

class Futuur(PredictionSite):

    PLATFORM_NAME="Futuur"
    BROWSER_TEMPLATE=Template('https://futuur.com/q/$id')
    API_TEMPLATE=Template('https://api.futuur.com/v1.4/questions/$id')

    def __init__(self, url, yes_option=None, no_option=None):
        yes_option = yes_option or "YES"
        no_option = no_option or "NO"
        self._url = url
        # Example url: https://futuur.com/q/169063/will-meta-amazon-apple-google-twitter-tesla-or-netflix-begin-to-accept-crypto-as-payment-by-the-end-of-2023
        # Use regex to grab the number after the q/ and before the /
        self._market_id = str(re.search(r"q/([^/]+)", url).group(1))
        self._details = None
        self._yes_option = yes_option
        self._no_option = no_option

    def is_real_money(self):
        return True

    def details(self):
        if not self._details:
            details_url = Futuur.API_TEMPLATE.substitute(id=self.market_id())
            self._details = requests.get(details_url).json()
        return self._details

    def title(self):
        return self.details()['title']

    def probability(self):
        yes_option = self._get_yes_option()
        assert yes_option, "Error: Could not find yes option (" + self._yes_option + ") in Futuur market: " + self._url
        return yes_option['price']['BTC']


    """ Unfortunately, the faq doesn't tell us the formula for the fees. With some experimentation, the fees are around:
      PROB  FEE
      .5 -> .08
      .96 -> .98
      .01 -> <.01
      A formula that approximates this is:
        fee = prob * (.22 - .22*prob*prob)
    """
    def fee_adjustment(self, buying_yes):
        prob = self.probability()
        inversion = 1
        if not buying_yes:
            prob = 1 - prob
            inversion = -1
        return inversion * prob * (.22 - .22*prob*prob)

    def size(self):
        return int(self.details()['volume_real_money'])

    def size_string(self):
        return Style.BOLD + '$  ' + Style.reset + str(self.size())

    def close_time(self):
        # Close time is for example "2031-01-01T00:00:00Z", convert to datetime
        return datetime.fromisoformat(self.details()["bet_end_date"][:-1])

    def is_binary(self):
        return self._get_yes_option() and self._get_no_option()

    def is_open(self):
        deets = self.details()
        return self.is_binary() and \
            not self._get_yes_option()['disabled'] and \
            not self._get_no_option()['disabled'] and \
            deets['wagerable'] and \
            deets['real_currency_available'] and \
            deets['resolution'] == None


    def _get_yes_option(self):
        if not 'outcomes' in self.details():
            print("Error: Could not find outcomes in Futuur market: " + self._url)
            print("details: " + str(self.details()))
        for outcome in self.details()['outcomes']:
            # Compare case insesitive
            if not 'title' in outcome:
                print("Error: Could not find title in outcome: " + str(outcome))
            if outcome['title'].lower() == self._yes_option.lower():
                return outcome
        print("Error: Could not find yes option (" + self._yes_option + ") in Futuur market: " + self._url)
        print("Outcomes: " + str(self.details()['outcomes']))
        return None

    def _get_no_option(self):
        for outcome in self.details()['outcomes']:
            if outcome['title'] == self._no_option:
                return outcome
        return None

    def color(self, text):
        return Fore.BLUE + Style.BOLD + text + Style.reset
