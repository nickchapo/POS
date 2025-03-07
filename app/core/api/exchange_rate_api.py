import requests


class ExchangeRateAPI:
    BASE_URL = "https://v6.exchangerate-api.com/v6"
    API_KEY = "7ebaad9da68d5cb07d43fd59"

    def get_rate_data(self, base_currency: str, target_currency: str) -> dict:
        url = f"{self.BASE_URL}/{self.API_KEY}/pair/{base_currency}/{target_currency}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
