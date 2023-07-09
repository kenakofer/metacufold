class PredictionSite:
    def __init__(self):
        raise NotImplementedError("Inheriting class must implement this")

    def url(self):
        return self._url

    def color(self, text):
        raise NotImplementedError("Inheriting class must implement this")

    def market_id(self):
        return self._market_id

    def details(self):
        raise NotImplementedError("Inheriting class must implement this")

    def title(self):
        raise NotImplementedError("Inheriting class must implement this")

    def probability(self):
        raise NotImplementedError("Inheriting class must implement this")

    def size(self):
        raise NotImplementedError("Inheriting class must implement this")

    def close_time(self):
        raise NotImplementedError("Inheriting class must implement this")

    def is_binary(self):
        raise NotImplementedError("Inheriting class must implement this")

    def is_open(self):
        raise NotImplementedError("Inheriting class must implement this")

    def market_link(string):
        raise NotImplementedError("Inheriting class must implement this")

    def user_position_shares(self):
        # If not supported, default 0
        return 0

    def __str__(self):
        return self.title() + " (" + self.url() + ")"
