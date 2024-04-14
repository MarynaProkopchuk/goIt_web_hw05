import platform

import sys
from datetime import datetime, timedelta

import aiohttp
import asyncio

currency = ["USD", "EUR"]
available_currency = []


async def request(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data
                else:
                    print(f"Error status: {resp.status} for {url}")
        except (aiohttp.ClientConnectorError, aiohttp.InvalidURL) as err:
            print(f"Connection error: {url}", str(err))


def get_available_currency(data: dict):
    for x in data["exchangeRate"]:
        available_currency.append(x["currency"])
    return available_currency


def parser(data: dict):
    exchange_list = {}
    for x in data["exchangeRate"]:
        if x["currency"] in currency:
            y = {
                x["currency"]: {
                    "sale": x["saleRateNB"],
                    "purchase": x["purchaseRateNB"],
                }
            }
            exchange_list.update(y)
    return exchange_list


async def main(index_day: str, additional_currency=None):
    index_day = int(index_day)
    if 0 < index_day <= 10:
        result = []
        for x in range(0, index_day):
            d = datetime.now() - timedelta(days=(index_day - 1))
            shift = d.strftime("%d.%m.%Y")
            response = await request(
                f"https://api.privatbank.ua/p24api/exchange_rates?date={shift}"
            )
            get_available_currency(response)
            if additional_currency in available_currency:
                currency.append(additional_currency)
                result.append({shift: parser(response)})
                index_day -= 1
            elif additional_currency == None:
                result.append({shift: parser(response)})
                index_day -= 1
        return result
    else:
        return "Sorry, i can only show you the exchange rate of the last 10 days"


if __name__ == "__main__":
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    if len(sys.argv) == 2:
        r = asyncio.run(main(sys.argv[1]))
        print(r)
    elif len(sys.argv) == 3:
        r = asyncio.run(main(sys.argv[1], sys.argv[2]))
        print(r)
    else:
        print("input error")
