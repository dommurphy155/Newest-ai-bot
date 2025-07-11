from oandapyV20.endpoints.instruments import InstrumentsCandles
from oandapyV20 import API
import os

def fetch_oanda_candles(instrument="EUR_USD", granularity="M5", count=100):
    api_key = os.environ.get("OANDA_API")
    client = API(access_token=api_key)
    params = {
        "granularity": granularity,
        "count": count,
        "price": "M"
    }
    r = InstrumentsCandles(instrument=instrument, params=params)
    client.request(r)
    candles = r.response["candles"]
    return candles
