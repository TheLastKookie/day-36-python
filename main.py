import requests
import math
import os
from twilio.rest import Client

STOCK_DIFFERENCE = 2

STOCKS = {
    "apple": "AAPL",
    "microsoft": "MSFT",
    "nvidia": "NVDA",
    "amazon": "AMZN",
}

STOCK_API_KEY = os.environ.get("STOCK_API_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
TWILIO_SID = os.environ.get("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.environ.get("TWILIO_PHONE")
TO_PHONE = os.environ.get("TO_PHONE")


def find_difference(v1, v2):
    if v1 == v2:
        return 0
    else:
        return math.floor((abs(v1 - v2) / ((v1 + v2) / 2)) * 100)


def get_stock(stock):
    stock_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=" \
                f"{STOCKS[stock]}&apikey={STOCK_API_KEY} "
    stock_response = requests.get(stock_url)
    stock_response.raise_for_status()
    daily_stock = stock_response.json()["Time Series (Daily)"]
    dates = [date for date in daily_stock]

    yesterday_stock_close = float(daily_stock[dates[0]]["4. close"])
    day_before_stock_close = float(daily_stock[dates[1]]["4. close"])

    difference = find_difference(yesterday_stock_close, day_before_stock_close)
    if difference >= STOCK_DIFFERENCE:
        news_url = f"https://newsapi.org/v2/top-headlines?q={stock}&apiKey={NEWS_API_KEY}"
        news_response = requests.get(news_url)
        news_response.raise_for_status()
        top_three_articles = news_response.json()["articles"][:3]

        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        message = ""
        if not top_three_articles:
            if day_before_stock_close > yesterday_stock_close:
                message = f"{STOCKS[stock]}: 🔻{difference}%\nNo major headlines to report."
            else:
                message = f"{STOCKS[stock]}: 🔺{difference}%\nNo major headlines to report."
        else:
            for article in top_three_articles:
                if day_before_stock_close > yesterday_stock_close:
                    message = f"{STOCKS[stock]}: 🔻{difference}%\n"
                else:
                    message = f"{STOCKS[stock]}: 🔺{difference}%\n"
                message = message + f"Headline: {article['title']}\nBrief: {article['description']}"

        message_send = client.messages.create(
            body=f"{message}",
            from_=f"{TWILIO_PHONE}",
            to=f"{TO_PHONE}"
        )

        print(message_send.status)


for stock in STOCKS:
    get_stock(stock)
