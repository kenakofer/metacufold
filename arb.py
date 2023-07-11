import config as C
from functools import reduce
from datetime import datetime

class Order:
    TOP = 1
    BOTTOM = 2
    MIDDLE = 3

NOVELTY_WEIGHT = 2.0

class Arb:
    def __init__(self, markets, fuzz_factors=None):
        if fuzz_factors is None:
            fuzz_factors = [1] * len(markets)
        assert len(markets) == len(fuzz_factors), "Number of markets and fuzz factors must be equal"
        self._markets = [ArbMarket(m, f) for m, f in zip(markets, fuzz_factors)]
        self._markets.sort(key=lambda am: am.market.probability())
        self._markets[0].order = Order.TOP
        self._markets[-1].order = Order.BOTTOM
        self._arb_score = None
        self._arb_score = self.score()

    def markets(self):
        return [am.market for am in self._markets]

    def arb_markets(self):
        return self._markets[:]

    def score(self, markets=None):
        """
        Returns a score for a given arb, which is based on the difference in probabilities and the size of the markets.
        """
        if self._arb_score is not None:
            return self._arb_score

        if markets is None:
            markets = self.markets()

        # Size score is the product of the sizes of the markets, root the number of markets
        size_score = reduce(lambda x, y: x * y, [m.size() for m in markets], 1)
        size_score **= (1 / len(markets))

        bound = lambda x: min(max(x, 0.005), 0.995)

        lower = bound(markets[0].probability() + markets[0].fee_adjustment(True))
        upper = bound(markets[-1].probability() + markets[-1].fee_adjustment(False))

        if lower > upper:
            if (len(markets) < 3):
                spread_score = .01 # If there are only two markets, we can't remove one, so just give it a lowish spread score
            elif (markets[0].fee_adjustment(True) < markets[-1].fee_adjustment(False)):
                # Return the arb score without the higher-fee upper market
                return self.score(markets[:-1])
            else:
                # Return the arb score without the higher-fee lower market
                return self.score(markets[1:])
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
        return self._arb_score


class ArbMarket:
    def __init__(self, market, fuzz_factor):
        self.market = market
        self.fuzz_factor = fuzz_factor
        self.order = Order.MIDDLE

    def fee_adjustment(self):
        if self.order == Order.MIDDLE:
            return 0
        return self.market.fee_adjustment(self.order == Order.TOP)

    def __str__(self):
        return str(self.market) + " (fuzz factor: " + str(self.fuzz_factor) + ")"