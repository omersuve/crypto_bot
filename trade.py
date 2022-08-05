from tradingview_ta import TA_Handler, Interval, Exchange
from datetime import datetime, timedelta
import schedule
import time
import requests

total_fails = 0
total_profit_opportunities = 0
latest_prices_dict = {}
telegram_base_url = "https://api.telegram.org/bot5448377023:AAGbz5kG6r2HcFZdWMhe7wj1lQl9sKLRN4E/sendMessage?chat_id=-600005362&text={}"

symbols = [
    "BTCUSDT",
    "ETHUSDT",
    "ALICEUSDT",
    "ATOMUSDT",
    "FTMUSDT",
    "AUDIOUSDT",
    "GRTUSDT",
    "CHZUSDT",
    "KLAYUSDT",
    "MINAUSDT",
]


def calculate_profit(recc, old_price, current_price, total_profit_opportunities):
    requests.get(
        telegram_base_url.format(
            "if you had {}, A profit may have been earned!".format(recc)
        )
    )
    requests.get(
        telegram_base_url.format(
            "%{}".format(
                str(
                    abs((float(current_price) - float(old_price)) / float(old_price))
                    * 100
                )
            )
        )
    )
    total_profit_opportunities = total_profit_opportunities + 1
    return total_profit_opportunities


def fail_reccommend(recc, old_price, current_price, total_fails):
    requests.get(
        telegram_base_url.format(
            "if you had {}, A loss may have been occured!".format(recc)
        )
    )
    requests.get(
        telegram_base_url.format(
            "%{}".format(
                str(
                    abs((float(current_price) - float(old_price)) / float(old_price))
                    * 100
                )
            )
        )
    )
    total_fails = total_fails + 1
    return total_fails


def process():
    global total_fails
    global total_profit_opportunities
    for symbol in symbols:
        output = TA_Handler(
            symbol=symbol,
            screener="Crypto",
            exchange="Binance",
            interval=Interval.INTERVAL_4_HOURS,
        )
        recc = output.get_analysis().summary["RECOMMENDATION"]
        print("{} // {}".format(symbol, recc))
        requests.get(telegram_base_url.format("{} // {}".format(symbol, recc)))

        json_res = requests.get(
            "https://www.binance.com/api/v3/ticker/price?symbol={}".format(symbol)
        ).json()

        price_of_symbol = json_res["price"]
        print(price_of_symbol + "\n************")
        requests.get(telegram_base_url.format(price_of_symbol))

        if recc == "BUY" or recc == "STRONG_BUY":
            if (
                latest_prices_dict[symbol][1] == "SELL"
                or latest_prices_dict[symbol][1] == "STRONG_SELL"
            ):
                if latest_prices_dict[symbol][0] < price_of_symbol:
                    total_fails = fail_reccommend(
                        latest_prices_dict[symbol][1],
                        latest_prices_dict[symbol][0],
                        price_of_symbol,
                        total_fails,
                    )
                elif latest_prices_dict[symbol][0] > price_of_symbol:
                    total_profit_opportunities = calculate_profit(
                        latest_prices_dict[symbol][1],
                        latest_prices_dict[symbol][0],
                        price_of_symbol,
                        total_profit_opportunities,
                    )
        elif recc == "SELL" or recc == "STRONG_SELL":
            if (
                latest_prices_dict[symbol][1] == "BUY"
                or latest_prices_dict[symbol][1] == "STRONG_BUY"
            ):
                if latest_prices_dict[symbol][0] > price_of_symbol:
                    total_fails = fail_reccommend(
                        latest_prices_dict[symbol][1],
                        latest_prices_dict[symbol][0],
                        price_of_symbol,
                        total_fails,
                    )
                elif latest_prices_dict[symbol][0] < price_of_symbol:
                    total_profit_opportunities = calculate_profit(
                        latest_prices_dict[symbol][1],
                        latest_prices_dict[symbol][0],
                        price_of_symbol,
                        total_profit_opportunities,
                    )

        latest_prices_dict[symbol] = [price_of_symbol, recc]

    print("total_fails:", total_fails)
    print("total_profit_opportunities:", total_profit_opportunities)


for symbol in symbols:
    output = TA_Handler(
        symbol=symbol,
        screener="Crypto",
        exchange="Binance",
        interval=Interval.INTERVAL_4_HOURS,
    )
    recc = output.get_analysis().summary["RECOMMENDATION"]
    latest_prices_dict[symbol] = [0, ""]
    latest_prices_dict[symbol][1] = recc

    json_res = requests.get(
        "https://www.binance.com/api/v3/ticker/price?symbol={}".format(symbol)
    ).json()

    latest_prices_dict[symbol][0] = json_res["price"]

print(latest_prices_dict)

schedule.every(30).minutes.do(process)

while True:
    schedule.run_pending()
    time.sleep(1)
