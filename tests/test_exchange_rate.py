import pytest

from app.infra.core.adapter.economia_exchange_rate_adapter import EconomiaExchangeRateAdapter
from app.infra.core.currency import Currency

def test_get_exchange_rate_valid(monkeypatch):
    def fake_get_rate_data(base, target):
        return {"from": base, "to": target, "rate": 0.86}

    adapter = EconomiaExchangeRateAdapter()
    monkeypatch.setattr(adapter.api, "get_rate_data", fake_get_rate_data)

    rate = adapter.get_exchange_rate(Currency.USD, Currency.EUR)
    assert isinstance(rate, float)
    assert rate == 0.86

def test_get_exchange_rate_missing_rate(monkeypatch):
    def fake_get_rate_data(base, target):
        return {"from": base, "to": target}

    adapter = EconomiaExchangeRateAdapter()
    monkeypatch.setattr(adapter.api, "get_rate_data", fake_get_rate_data)

    with pytest.raises(ValueError, match="No valid rate found"):
        adapter.get_exchange_rate(Currency.USD, Currency.EUR)

def test_get_exchange_rate_none_rate(monkeypatch):
    def fake_get_rate_data(base, target):
        return {"from": base, "to": target, "rate": None}

    adapter = EconomiaExchangeRateAdapter()
    monkeypatch.setattr(adapter.api, "get_rate_data", fake_get_rate_data)

    with pytest.raises(ValueError, match="No valid rate found"):
        adapter.get_exchange_rate(Currency.USD, Currency.EUR)
