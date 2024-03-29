class PredictionSite:

    PLATFORM_NAME = "PLATFORM_NAME NOT_SET"

    def __init__(self):
        raise NotImplementedError("Inheriting class must implement this")

    def url(self):
        return self._url

    def is_real_money(self):
        raise NotImplementedError("Inheriting class must implement this")

    def color(self, text):
        raise NotImplementedError("Inheriting class must implement this")

    def market_id(self):
        return self._market_id

    def details(self, invalidate_cache=False):
        raise NotImplementedError("Inheriting class must implement this")

    def title(self):
        raise NotImplementedError("Inheriting class must implement this")

    def probability(self):
        raise NotImplementedError("Inheriting class must implement this")

    def fee_adjustment(self, buying_yes):
        return 0

    def size(self):
        raise NotImplementedError("Inheriting class must implement this")

    def size_string(self):
        return str(self.size())

    def close_time(self):
        raise NotImplementedError("Inheriting class must implement this")

    def is_binary(self):
        raise NotImplementedError("Inheriting class must implement this")

    def can_bet_down(self):
        raise NotImplementedError("Inheriting class must implement this")

    def is_open(self):
        raise NotImplementedError("Inheriting class must implement this")

    def market_link(string):
        raise NotImplementedError("Inheriting class must implement this")

    def user_position_shares(self, invalidate_cache=False, error_value=0):
        # If not supported, default 0
        return 0

    def open_url(self):
        import webbrowser
        webbrowser.open(self.url())

    def refresh(self):
        details = self.details(invalidate_cache=True)
        position = self.user_position_shares(invalidate_cache=True)
        print("New probability: " + str(self.probability()))
        print("New position: " + str(self.user_position_shares()))

    def __str__(self):
        return self.title() + " (" + self.url() + ")"
