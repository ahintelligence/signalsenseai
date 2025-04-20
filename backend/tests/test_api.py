# backend/tests/test_api.py

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.mark.parametrize("ticker,expected_status", [
    ("AAPL", 200),
    ("INVALIDTICKER", 404),
])
def test_predict_endpoint(ticker, expected_status):
    res = client.get(f"/predict/{ticker}")
    assert res.status_code == expected_status
    data = res.json()
    if expected_status == 200:
        assert "ticker" in data and data["ticker"] == ticker.upper()
        assert "signal" in data and data["confidence"] >= 0
    else:
        assert "detail" in data

def test_history_endpoint():
    res = client.get("/history/AAPL?range=1mo")
    assert res.status_code == 200
    data = res.json()
    assert data["ticker"] == "AAPL"
    assert isinstance(data["history"], list)
    # each record should have OHLC fields
    for rec in data["history"][:3]:
        for key in ("open", "high", "low", "close", "date"):
            assert key in rec

def test_latest_price_endpoint():
    res = client.get("/latest-price/AAPL")
    assert res.status_code == 200
    data = res.json()
    for key in ("open", "high", "low", "close", "date"):
        assert key in data

def test_history_bad_range():
    res = client.get("/history/AAPL?range=foo")
    assert res.status_code == 400
    assert "error" in res.json()
