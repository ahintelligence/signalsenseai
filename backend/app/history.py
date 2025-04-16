import yfinance as yf
import pandas as pd
from fastapi.responses import JSONResponse

def get_price_history(ticker: str, range: str = "1mo"):
    try:
        df = yf.download(ticker, period=range, interval="1d", auto_adjust=True)

        if df.empty:
            return JSONResponse(status_code=404, content={"error": f"No data found for {ticker}"})

        # Handle multi-level column names
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join(filter(None, col)).strip() for col in df.columns.values]

        # Identify the close column
        close_col = next((col for col in df.columns if 'close' in col.lower()), None)
        if not close_col:
            raise KeyError("No 'Close' column found in the downloaded data.")

        df = df[[close_col]].reset_index()
        df.rename(columns={close_col: 'Close'}, inplace=True)

        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        df['Close'] = df['Close'].astype(float)

        history_data = df.to_dict(orient="records")

        return JSONResponse(content={
            "ticker": ticker.upper(),
            "range": range,
            "history": history_data
        })

    except Exception as e:
        print("🔴 Error in get_price_history:", str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})




