import yfinance as yf
import pandas as pd
from fastapi.responses import JSONResponse

def get_price_history(ticker: str, range: str = "1mo"):
    try:
        df = yf.download(ticker, period=range, interval="1d", auto_adjust=False)

        if df.empty:
            return JSONResponse(status_code=404, content={"error": f"No data found for {ticker}"})

        df = df.reset_index()

        # Flatten MultiIndex columns if they exist
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join(filter(None, col)).strip() for col in df.columns.values]

        # Now look for the expected column names
        expected_cols = ["Date", f"Open_{ticker.upper()}", f"High_{ticker.upper()}",
                         f"Low_{ticker.upper()}", f"Close_{ticker.upper()}"]

        # Confirm all required columns exist
        missing_cols = [col for col in expected_cols if col not in df.columns]
        if missing_cols:
            return JSONResponse(status_code=500, content={"error": f"Missing columns in DataFrame: {df.columns.tolist()}"})

        # Select and rename to standard format
        df = df[["Date"] + expected_cols[1:]]
        df.columns = ["Date", "Open", "High", "Low", "Close"]

        df.dropna(inplace=True)

        # Format types
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
        for col in ["Open", "High", "Low", "Close"]:
            df[col] = df[col].astype(float)

        # Optional: add 20-period SMA
        df["SMA20"] = df["Close"].rolling(window=20).mean().round(2)
        df = df.dropna(subset=["SMA20"])  # removes NaN rows


        history_data = df.to_dict(orient="records")

        return JSONResponse(content={
            "ticker": ticker.upper(),
            "range": range,
            "history": history_data
        })

    except Exception as e:
        print("Error in get_price_history:", str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})







