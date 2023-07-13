import config as C
from functools import reduce
from datetime import datetime

class Order:
    TOP = 1
    BOTTOM = 2
    MIDDLE = 3

NOVELTY_WEIGHT = 2.0

class Arb:
    def __init__(self, markets, wiggle_factors=None, boost=0):
        if wiggle_factors is None:
            wiggle_factors = [0] * len(markets)
        assert len(markets) == len(wiggle_factors), "Number of markets and wiggle factors must be equal"
        self._arb_markets = [ArbMarket(m, f) for m, f in zip(markets, wiggle_factors)]
        self._boost = boost
        self._resort()

    def boost(self, amount):
        self._boost = amount
        self._resort()

    def markets(self):
        return [am.market for am in self._arb_markets]

    def _resort(self):
        if self._arb_markets:
            self._arb_markets.sort(key=lambda am: am.market.probability())
            self._arb_markets[0].order = Order.BOTTOM
            self._arb_markets[-1].order = Order.TOP
            self._arb_score = None
        self._arb_score = self.score()

    def remove_market(self, market):
        if isinstance(market, ArbMarket):
            self.remove_market(market.market)
            return
        self._arb_markets = [am for am in self._arb_markets if am.market != market]
        self._resort()

    def arb_markets(self):
        return self._arb_markets[:]

    def score(self, arb_markets=None):
        """
        Returns a score for a given arb, which is based on the difference in probabilities and the size of the markets.
        """
        if self._arb_score is not None:
            return self._arb_score

        if arb_markets is None:
            arb_markets = self._arb_markets

        if len(arb_markets) == 1:
            self._arb_score = 0
            return self._arb_score

        markets = [am.market for am in arb_markets]

        # Size score is the product of the sizes of the markets, root the number of markets
        size_score = reduce(lambda x, y: x * y, [m.size() for m in markets], 1)
        size_score **= (1 / len(markets))

        bound = lambda x: min(max(x, 0.005), 0.995)

        assert markets[0].probability() <= markets[-1].probability(), "Markets must be sorted by probability"
        lower = bound(markets[0].probability() + arb_markets[0].all_adjustments(True))
        upper = bound(markets[-1].probability() + arb_markets[-1].all_adjustments(False))

        # If the two cross, that means the adjustements are large enough that these two won't be arb-able.
        if lower > upper:
            if (len(arb_markets) < 3):
                spread_score = .01 # If there are only two markets, we can't remove one, so just give it a lowish spread score
            elif (arb_markets[0].all_adjustments(True) < arb_markets[-1].all_adjustments(False)):
                # Return the arb score without the higher-fee upper market
                return self.score(arb_markets[:-1])
            else:
                # Return the arb score without the higher-fee lower market
                return self.score(arb_markets[1:])
        else:
            spread_score = upper - lower # Upper - Lower should not be negative in this branch

        edginess_score = 1 / (upper * lower * (1 - upper) * (1 - lower))

        # Immanence score (if it closes sooner, it's better)
        immanence_score = 3600 * 24 * 365 / (markets[0].close_time() - datetime.now()).total_seconds()

        # Position score: if I'm holding a Manifold position, but Metaculus is the other way, we want to know about that and probably sell the position.
        position_score = 1
        if spread_score > 2:
            lower_shares = markets[0].user_position_shares()
            upper_shares = markets[-1].user_position_shares()
            if lower_shares < 0 or upper_shares > 0:
                position_score = 10000
            elif lower_shares == 0 and upper_shares == 0:
                position_score = NOVELTY_WEIGHT

        # print(size_score, spread_score, edginess_score, immanence_score)

        self._arb_score = size_score * spread_score**3 * edginess_score * immanence_score**.5 * position_score

        self._arb_score += self._boost
        return self._arb_score


class ArbMarket:
    def __init__(self, market, wiggle_factor=0):
        self.market = market
        self.order = Order.MIDDLE
        self.wiggle = wiggle_factor

    def fee_adjustment(self, buying_yes=None):
        if buying_yes is None:
            buying_yes = self.order == Order.BOTTOM
        if self.order == Order.MIDDLE:
            return 0
        return self.market.fee_adjustment(buying_yes)

    def wiggle_adjustment(self, buying_yes=None):
        if self.wiggle == 0:
            return 0
        if buying_yes is None:
            buying_yes = self.order == Order.BOTTOM
        prob = self.market.probability()
        inversion = 1
        if not buying_yes:
            prob = 1 - prob
            inversion = -1
        return inversion * (1-prob) * self.wiggle

    def all_adjustments(self, buying_yes=None):
        return self.fee_adjustment(buying_yes) + self.wiggle_adjustment(buying_yes)


    def __str__(self):
        return str(self.market) + " (wiggle factor: " + str(self.wiggle) + ")"