from abc import ABC, abstractmethod

from app.core.currency import Currency


class ExchangeRateTarget(ABC):
    @abstractmethod
    def get_exchange_rate(
        self, base_currency: Currency, target_currency: Currency
    ) -> float:
        pass
