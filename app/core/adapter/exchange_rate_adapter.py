from app.core.adapter.exchange_rate_target import ExchangeRateTarget
from app.core.api.exchange_rate_api import ExchangeRateAPI
from app.core.currency import Currency


class ExchangeRateAdapter(ExchangeRateTarget):
    def __init__(self):
        self.api = ExchangeRateAPI()

    def get_exchange_rate(
        self, base_currency: Currency, target_currency: Currency
    ) -> float:
        base = (
            base_currency.value
            if isinstance(base_currency, Currency)
            else base_currency
        )
        target = (
            target_currency.value
            if isinstance(target_currency, Currency)
            else target_currency
        )
        data = self.api.get_rate_data(base, target)

        if "conversion_rate" not in data or data["conversion_rate"] is None:
            raise ValueError(f"No valid rate found for {base} to {target}.")

        return float(data["conversion_rate"])
