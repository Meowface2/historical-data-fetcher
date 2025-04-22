import os
import requests
import pandas as pd
from datetime import datetime, timezone

# ── CONFIG ─────────────────────────────────────────────────────────────────────
START_DATE = "2024-06-22"
END_DATE   = "2025-04-17"

# 1) BITO via Alpha Vantage CSV endpoint
ALPHA_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
bito_url  = "https://www.alphavantage.co/query"
params    = {
    "function":   "TIME_SERIES_DAILY_ADJUSTED",
    "symbol":     "BITO",
    "outputsize": "full",
    "datatype":   "csv",
    "apikey":     ALPHA_KEY,
}
df_bito = pd.read_csv(requests.get(bito_url, params=params).text)
df_bito["timestamp"] = pd.to_datetime(df_bito["timestamp"])
df_bito = df_bito[
    (df_bito["timestamp"] >= START_DATE) &
    (df_bito["timestamp"] <= END_DATE)
]
df_bito.to_csv("BITO_historical.csv", index=False)

# 2) BTC via Binance klines JSON
binance_url = "https://api.binance.com/api/v3/klines"
start_ms    = int(datetime.fromisoformat(START_DATE)
                      .replace(tzinfo=timezone.utc)
                      .timestamp() * 1000)
end_ms      = int(datetime.fromisoformat(END_DATE)
                      .replace(tzinfo=timezone.utc)
                      .timestamp() * 1000)
params = {
    "symbol":    "BTCUSDT",
    "interval":  "1d",
    "startTime": start_ms,
    "endTime":   end_ms,
}
klines = requests.get(binance_url, params=params).json()

# name columns & build DataFrame
cols = [
    "OpenTime", "Open", "High", "Low", "Close", "Volume",
    "CloseTime", "QuoteAssetVolume", "NumTrades",
    "TakerBuyBaseVol", "TakerBuyQuoteVol", "Ignore"
]
df_btc = pd.DataFrame(klines, columns=cols)
df_btc["Date"] = pd.to_datetime(df_btc["OpenTime"], unit="ms").dt.date
df_btc = df_btc[["Date","Open","High","Low","Close","Volume"]]
df_btc.to_csv("BTC_historical.csv", index=False)
