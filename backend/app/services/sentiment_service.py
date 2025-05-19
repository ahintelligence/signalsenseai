import os
import time
import logging
import requests
import tweepy
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Setup sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Setup logger and cache
logger = logging.getLogger(__name__)
os.makedirs("cache", exist_ok=True)

# Environment configs
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
NEWS_URL = "https://newsapi.org/v2/everything"

# Tweepy client
client = tweepy.Client(bearer_token=BEARER_TOKEN) if BEARER_TOKEN else None

# ─────────────────────────────────────────────────────────────

def get_social_sentiment_series(query: str, days: int = 7, max_results: int = 100, force_refresh: bool = False) -> pd.Series:
    """
    Pulls social sentiment data from Twitter using VADER, falls back to simulated data if unavailable.
    """
    cache_path = f"cache/social_sentiment_{query.lower()}.csv"

    if os.path.exists(cache_path) and not force_refresh:
        try:
            return pd.read_csv(cache_path, index_col="date", parse_dates=True).squeeze("columns")
        except Exception as e:
            logger.warning(f"⚠️ Failed to load social sentiment cache: {e}")

    if not client:
        logger.warning("⚠️ Twitter API unavailable — simulating sentiment.")
        return _simulate_sentiment(query, days, cache_path)

    now = datetime.utcnow().replace(microsecond=0)
    end_time = now - timedelta(seconds=20)
    start_time = now - timedelta(days=days, seconds=60)

    records = []

    try:
        paginator = tweepy.Paginator(
            client.search_recent_tweets,
            query=query,
            start_time=start_time.isoformat("T") + "Z",
            end_time=end_time.isoformat("T") + "Z",
            tweet_fields=["created_at"],
            max_results=100
        )

        for tweet in paginator.flatten(limit=max_results):
            try:
                if tweet.text:
                    sentiment = analyzer.polarity_scores(tweet.text)["compound"]
                    records.append({
                        "date": tweet.created_at.date(),
                        "sentiment": sentiment
                    })
                    time.sleep(0.25)
            except Exception as inner:
                logger.warning(f"Error parsing tweet: {inner}")
                continue

    except tweepy.TooManyRequests:
        logger.warning("⚠️ Twitter rate limit hit — simulating sentiment.")
        return _simulate_sentiment(query, days, cache_path)
    except tweepy.TweepyException as e:
        logger.warning(f"⚠️ Tweepy exception: {e}")
        return _simulate_sentiment(query, days, cache_path)

    if not records:
        return _simulate_sentiment(query, days, cache_path)

    df = pd.DataFrame(records)
    df_grouped = df.groupby("date")["sentiment"].mean()
    df_grouped.to_csv(cache_path)
    return df_grouped


def get_news_sentiment_series(ticker: str, days: int = 7, max_articles: int = 50, force_refresh: bool = False) -> pd.Series:
    """
    Pulls recent news headlines and analyzes sentiment using VADER.
    Cached daily per ticker.
    """
    cache_path = f"cache/news_sentiment_{ticker.lower()}.csv"

    if os.path.exists(cache_path) and not force_refresh:
        try:
            return pd.read_csv(cache_path, index_col="date", parse_dates=True).squeeze("columns")
        except Exception as e:
            logger.warning(f"⚠️ Failed to load news sentiment cache: {e}")

    if not NEWSAPI_KEY:
        logger.warning("⚠️ Missing NEWSAPI_KEY. Returning empty sentiment.")
        return pd.Series(dtype=float)

    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days)

    params = {
        "q": ticker,
        "from": start_date.isoformat(),
        "to": end_date.isoformat(),
        "language": "en",
        "sortBy": "relevancy",
        "pageSize": max_articles,
        "apiKey": NEWSAPI_KEY
    }

    try:
        response = requests.get(NEWS_URL, params=params, timeout=10)
        data = response.json()
    except Exception as e:
        logger.warning(f"⚠️ News fetch failed: {e}")
        return pd.Series(dtype=float)

    if response.status_code != 200 or "articles" not in data:
        logger.warning(f"⚠️ Failed to fetch news articles: {data}")
        return pd.Series(dtype=float)

    records = []
    for article in data["articles"][:max_articles]:
        title = article.get("title", "")
        date = pd.to_datetime(article["publishedAt"]).date()
        if title:
            sentiment = analyzer.polarity_scores(title)["compound"]
            records.append({"date": date, "sentiment": sentiment})

    if not records:
        return pd.Series(dtype=float)

    df = pd.DataFrame(records)
    df_grouped = df.groupby("date")["sentiment"].mean()
    df_grouped.to_csv(cache_path)
    return df_grouped


def _simulate_sentiment(query: str, days: int, cache_path: str) -> pd.Series:
    logger.warning("⚠️ Generating simulated sentiment fallback...")

    end_date = datetime.utcnow().date()
    dates = [end_date - timedelta(days=i) for i in range(days)][::-1]
    sentiments = np.random.uniform(-0.2, 0.2, size=days)

    df = pd.DataFrame({"date": dates, "sentiment": sentiments})
    df.set_index("date", inplace=True)
    df.to_csv(cache_path)
    return df.squeeze("columns")




