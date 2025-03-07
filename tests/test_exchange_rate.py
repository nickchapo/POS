import pytest

from app.core.adapter.exchange_rate_adapter import ExchangeRateAdapter
from app.core.currency import Currency


def test_get_exchange_rate_valid(monkeypatch):
    def fake_get_rate_data(base, target):
        return {"base_code": base, "target_code": target, "conversion_rate": 0.86}

    adapter = ExchangeRateAdapter()
    monkeypatch.setattr(adapter.api, "get_rate_data", fake_get_rate_data)

    rate = adapter.get_exchange_rate(Currency.USD, Currency.EUR)
    assert isinstance(rate, float)
    assert rate == 0.86


def test_get_exchange_rate_missing_rate(monkeypatch):
    def fake_get_rate_data(base, target):
        return {"base_code": base, "target_code": target}

    adapter = ExchangeRateAdapter()
    monkeypatch.setattr(adapter.api, "get_rate_data", fake_get_rate_data)

    with pytest.raises(ValueError, match="No valid rate found"):
        adapter.get_exchange_rate(Currency.USD, Currency.EUR)


def test_get_exchange_rate_none_rate(monkeypatch):
    def fake_get_rate_data(base, target):
        return {"base_code": base, "target_code": target, "conversion_rate": None}

    adapter = ExchangeRateAdapter()
    monkeypatch.setattr(adapter.api, "get_rate_data", fake_get_rate_data)

    with pytest.raises(ValueError, match="No valid rate found"):
        adapter.get_exchange_rate(Currency.USD, Currency.EUR)
