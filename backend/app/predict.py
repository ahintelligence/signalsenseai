from fastapi import HTTPException
from app.model import load_model, generate_features
from app.data import get_stock_data
from app.explain import explain_signal
from app.utils import safe_serialize

def get_prediction(ticker: str):
    try:
        df = get_stock_data(ticker)
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for ticker '{ticker.upper()}'.")

        X, _ = generate_features(df)
        if X.empty:
            raise HTTPException(status_code=400, detail="Feature generation failed — not enough data.")

        model = load_model(ticker)
        latest = X.iloc[-1:].values

        prediction = model.predict(latest)[0]
        probability = model.predict_proba(latest)[0][int(prediction)]

        # Format confidence
        raw_confidence = float(probability)
        confidence_pct = f"{round(raw_confidence * 100, 2)}"

        signal = "Buy" if prediction else "Hold/Sell"
        explanation = explain_signal(X)

        response = {
            "ticker": ticker.upper(),
            "signal": signal,
            "confidence": confidence_pct,
            "explanation": explanation
        }

        return safe_serialize(response)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

 



