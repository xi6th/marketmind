from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import requests
import pandas as pd

app = FastAPI()

API_KEY = "2T5P1F3YSOVKJBLD"
BASE_URL = "https://www.alphavantage.co/query"
VALID_INTERVALS = ["1min", "5min", "15min", "30min", "60min"]


def fetch_from_alpha_vantage(params: dict):
    params["apikey"] = API_KEY
    response = requests.get(BASE_URL, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Alpha Vantage API error")
    return response.json()


@app.get("/")
def root():
    return {"message": "Welcome to the Alpha Vantage Stock API - Use /intraday/{symbol}?interval=1min or /quote/{symbol}"}


@app.get("/intraday/{symbol}")
def get_intraday_data(
    symbol: str,
    interval: str = Query("1min", description="Time interval", enum=VALID_INTERVALS)
):
    if interval not in VALID_INTERVALS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid interval. Choose from: {', '.join(VALID_INTERVALS)}"
        )

    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": interval,
        "outputsize": "compact"
    }
    data = fetch_from_alpha_vantage(params)

    time_series_key = f"Time Series ({interval})"
    if time_series_key not in data:
        return JSONResponse(
            status_code=404,
            content={"error": "Intraday data not found. Try again later or check your symbol/interval."}
        )

    try:
        df = pd.DataFrame.from_dict(data[time_series_key], orient='index')
        df = df.astype(float)
        df.index = pd.to_datetime(df.index)
        df = df.rename(columns={
            "1. open": "open",
            "2. high": "high",
            "3. low": "low",
            "4. close": "close",
            "5. volume": "volume"
        })
        df = df.sort_index(ascending=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing data: {str(e)}")

    return {
        "symbol": symbol.upper(),
        "interval": interval,
        "latest_data": df.head(5).to_dict(orient="index"),
        "statistics": df.describe().to_dict()
    }


@app.get("/quote/{symbol}")
def get_global_quote(symbol: str):
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol
    }
    data = fetch_from_alpha_vantage(params)

    quote_key = "Global Quote"
    if quote_key not in data or not data[quote_key]:
        return JSONResponse(
            status_code=404,
            content={"error": "Global quote data not found. Try again later or check your symbol."}
        )

    try:
        quote = data[quote_key]
        return {
            "symbol": symbol.upper(),
            "price": float(quote["05. price"]),
            "open": float(quote["02. open"]),
            "high": float(quote["03. high"]),
            "low": float(quote["04. low"]),
            "volume": int(quote["06. volume"]),
            "latest_trading_day": quote["07. latest trading day"],
            "previous_close": float(quote["08. previous close"]),
            "change": float(quote["09. change"]),
            "change_percent": quote["10. change percent"]
        }
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=500, detail=f"Error processing quote data: {str(e)}")


@app.get("/monthly-adjusted/{symbol}")
def get_monthly_adjusted(symbol: str):
    params = {
        "function": "TIME_SERIES_MONTHLY_ADJUSTED",
        "symbol": symbol
    }
    return fetch_from_alpha_vantage(params)


@app.get("/weekly/{symbol}")
def get_weekly(symbol: str):
    params = {
        "function": "TIME_SERIES_WEEKLY",
        "symbol": symbol
    }
    return fetch_from_alpha_vantage(params)


@app.get("/daily/{symbol}")
def get_daily(symbol: str):
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol
    }
    return fetch_from_alpha_vantage(params)


@app.get("/news-sentiment/{tickers}")
def get_news_sentiment(tickers: str):
    params = {
        "function": "NEWS_SENTIMENT",
        "tickers": tickers
    }
    return fetch_from_alpha_vantage(params)


@app.get("/top-gainers-losers")
def get_top_gainers_losers():
    params = {"function": "TOP_GAINERS_LOSERS"}
    return fetch_from_alpha_vantage(params)


@app.get("/currency-exchange-rate")
def get_currency_exchange_rate(from_currency: str, to_currency: str):
    params = {
        "function": "CURRENCY_EXCHANGE_RATE",
        "from_currency": from_currency,
        "to_currency": to_currency
    }
    return fetch_from_alpha_vantage(params)


@app.get("/fx-daily")
def get_fx_daily(from_symbol: str, to_symbol: str):
    params = {
        "function": "FX_DAILY",
        "from_symbol": from_symbol,
        "to_symbol": to_symbol
    }
    return fetch_from_alpha_vantage(params)


@app.get("/fx-weekly")
def get_fx_weekly(from_symbol: str, to_symbol: str):
    params = {
        "function": "FX_WEEKLY",
        "from_symbol": from_symbol,
        "to_symbol": to_symbol
    }
    return fetch_from_alpha_vantage(params)


@app.get("/fx-monthly")
def get_fx_monthly(from_symbol: str, to_symbol: str):
    params = {
        "function": "FX_MONTHLY",
        "from_symbol": from_symbol,
        "to_symbol": to_symbol
    }
    return fetch_from_alpha_vantage(params)


@app.get("/real-gdp")
def get_real_gdp(interval: str = Query("annual", enum=["annual", "quarterly"])):
    params = {
        "function": "REAL_GDP",
        "interval": interval
    }
    return fetch_from_alpha_vantage(params)


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running smoothly."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
