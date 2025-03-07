import requests


class EconomiaExchangeRateAPI:
    BASE_URL = "https://publicapi.dev/economia-awesome-api"

    def get_rate_data(self, base_currency: str, target_currency: str) -> dict:
        url = f"{self.BASE_URL}/api/exchange-rate/{base_currency}/{target_currency}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
