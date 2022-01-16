import requests
import os
from twilio.rest import Client
import re

# Find these values at https://twilio.com/user/account
# To set up environmental variables, see
# https://www.twilio.com/docs/usage/secure-credentials
# and https://www.twilio.com/blog/2017/01/how-to-set-environment-variables.html

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
receiver_phone_num = os.environ['MY_PHONE_NUM']
sender_phone_num = os.environ['TWILIO_TRIAL_PHONE_NUM']
stock_api_key = os.environ['STOCK_API_KEY']
news_api_key = os.environ['NEWS_API_KEY']

STOCK_NAME = "AAPL"
COMPANY_NAME = "Apple Inc"
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

stock_parameters = {
    'symbol': STOCK_NAME,
    'apikey': stock_api_key,
    "function": "TIME_SERIES_DAILY",
}

client = Client(account_sid, auth_token)

# Use https://www.alphavantage.co/documentation/#daily
# Request to Alpha Vantage API to
# retrieve closing stock price of yesterday and day before yesterday.

response = requests.get(STOCK_ENDPOINT, params=stock_parameters)
stock_data = response.json()
time_series_daily = stock_data["Time Series (Daily)"]

stock_data_list = [value for key, value in time_series_daily.items()]
yesterday_closing_price = float(stock_data_list[0]["4. close"])
day_before_yesterday_closing_price = float(stock_data_list[1]["4. close"])

price_diff = yesterday_closing_price - day_before_yesterday_closing_price
percentage_diff = round((price_diff / day_before_yesterday_closing_price) * 100, 2)

up_down = ""
if price_diff > 0:
    up_down = "🔺"
else:
    up_down = "🔻"


def remove_html_tags(text):
    """Remove html tags from a string"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


# When stock price increase/decreases by >= 1% between yesterday and the day before yesterday then send message

if abs(percentage_diff) > 1:
    news_parameters = {
        'q': COMPANY_NAME,
        # 'from':'2021-08-11',
        # 'sortBy':'popularity',
        'apiKey': news_api_key,
    }

    # Request to News API to retrieve first 3 news of the company
    news_data = requests.get(NEWS_ENDPOINT, params=news_parameters).json()
    articles = news_data['articles'][:3]
    saved_articles = [(article['title'], article['description']) for article in articles]

    for item in saved_articles:
        message_text = f"{STOCK_NAME} {up_down}{abs(percentage_diff)}%:\nHeadline: {item[0]} \nBrief: {remove_html_tags(item[1])}"
        message = client.messages.create(
            body=message_text,
            from_=sender_phone_num,
            to=receiver_phone_num,
        )

else:
    message = client.messages.create(
        body=f"There was no significant change in the {STOCK_NAME} stock price.",
        from_=sender_phone_num,
        to=receiver_phone_num,
    )