import ApiRequest
import re

class Bitbay:
    def __init__(self):
        self.__INFO = {
            "name": "BITBAY",
            "URL": "https://bitbay.net/API/Public/",
            "market_info_URL": "https://api.bitbay.net/rest/trading/ticker",
            "orderbook_endpoint": "orderbook.json",
            "upper_bound_currency": "EUR",
            "Fees": {
                "maker_taker_fees":
                    [{"upper_bound": 1250, "takerFee": 0.0043, "makerFee": 0.003},
                     {"upper_bound": 3750, "takerFee": 0.0042, "makerFee": 0.0029},
                     {"upper_bound": 7500, "takerFee": 0.0041, "makerFee": 0.0028},
                     {"upper_bound": 10000, "takerFee": 0.0040, "makerFee": 0.0028},
                     {"upper_bound": 15000, "takerFee": 0.0039, "makerFee": 0.0027},
                     {"upper_bound": 20000, "takerFee": 0.0038, "makerFee": 0.0026},
                     {"upper_bound": 25000, "takerFee": 0.0037, "makerFee": 0.0025},
                     {"upper_bound": 37500, "takerFee": 0.0036, "makerFee": 0.0025},
                     {"upper_bound": 50000, "takerFee": 0.0035, "makerFee": 0.0024},
                     {"upper_bound": 75000, "takerFee": 0.0034, "makerFee": 0.0023},
                     {"upper_bound": 100000, "takerFee": 0.0033, "makerFee": 0.0023},
                     {"upper_bound": 150000, "takerFee": 0.0032, "makerFee": 0.0022},
                     {"upper_bound": 200000, "takerFee": 0.0031, "makerFee": 0.0021},
                     {"upper_bound": 250000, "takerFee": 0.0030, "makerFee": 0.0020},
                     {"upper_bound": 375000, "takerFee": 0.0029, "makerFee": 0.0019},
                     {"upper_bound": 500000, "takerFee": 0.0028, "makerFee": 0.0018},
                     {"upper_bound": 625000, "takerFee": 0.0027, "makerFee": 0.0018},
                     {"upper_bound": 875000, "takerFee": 0.0026, "makerFee": 0.0018},
                     {"takerFee": 0.0025, "makerFee": 0.0017}]
            }
        }
        self.__withdrawal_fees = {
                "AAVE": 0.54000000,
                "ALG": 426.00000000,
                "AMLT": 1743.00000000,
                "BAT": 185.00000000,
                "BCC": 0.00100000,
                "BCP": 1237.00000000,
                "BOB": 11645.00000000,
                "BSV": 0.00300000,
                "BTC": 0.00050000,
                "BTG": 0.00100000,
                "COMP": 0.10000000,
                "DAI": 81.00000000,
                "DASH": 0.00100000,
                "DOT": 0.10000000,
                "EOS": 0.1000,
                "ETH": 0.02000000,
                "EXY": 520.00000000,
                "GAME": 479.00000000,
                "GGC": 112.00000000,
                "GNT": 403.00000000,
                "GRT": 84.00000000,
                "LINK": 2.70000000,
                "LML": 1500.00000000,
                "LSK": 0.30000000,
                "LTC": 0.00100000,
                "LUNA": 0.02000000,
                "MANA": 100.00000000,
                "MKR": 0.02500000,
                "NEU": 185.00000000,
                "NPXS": 46451.00000000,
                "OMG": 24.00000000,
                "PAY": 1523.00000000,
                "QARK": 1019.00000000,
                "REP": 3.20000000,
                "SRN": 5717.00000000,
                "SUSHI": 8.80000000,
                "TRX": 1.000000,
                "UNI": 2.50000000,
                "USDC": 200.000000,
                "USDT": 290.00000000,
                "XBX": 5508.00000000,
                "XIN": 5.00000000,
                "XLM": 0.0050000,
                "XRP": 0.100000,
                "XTZ": 0.100000,
                "ZEC": 0.00400000,
                "ZRX": 56.00000000
        }

    def get_highest_bid_in_fee_format(self, currencies: tuple[str, str]):
        market = ApiRequest.make_request(f'{self.__INFO["market_info_URL"]}/{currencies[0]}-{self.__INFO["upper_bound_currency"]}')
        if market is not None and market["status"] == "Ok":
            return market["ticker"]["highestBid"]
        else:
            raise Exception("There is no highest bid in this API, biggest fee will be used to calculate total money")

    def get_maker_taker_fee(self, money_in_quote_currency: float, market: tuple[str, str]):
        try:
            highest_bid = self.get_highest_bid_in_fee_format(market)
            total_money = money_in_quote_currency * highest_bid
            i = 0
            length = len(self.get_fees())
            while i < length - 2:
                if total_money > self.get_fees()["upper_bound"]:
                    i += 1
                else:
                    return (self.get_fees()[i]["takerFee"],self.get_fees()[i]["makerFee"])
            if i == length:
                return (self.get_fees()[length - 1]["takerFee"],self.get_fees()[length - 1]["makerFee"])
        except Exception:
            return (self.get_fees()[0]["takerFee"],self.get_fees()[0]["makerFee"])

    def get_withdrawal_fee(self, currency: str):
        return self.__withdrawal_fees[currency]

    def get_fees(self):
        return self.__INFO["Fees"]["maker_taker_fees"]

    def request_bids_and_asks(self, currencies: tuple[str, str]):
        offers = ApiRequest.make_request(
            f'{self.__INFO["URL"]}{currencies[0]}{currencies[1]}/{self.__INFO["orderbook_endpoint"]}')

        if offers is not None:
            bids = offers["bids"]
            asks = offers["asks"]

            offers_dict = dict()
            offers_dict["bid"] = []
            offers_dict["ask"] = []

            if bids is not []:
                for item in bids:
                    offers_dict["bid"].append({"quantity": item[1], "rate": item[0]})

            if asks is not []:
                for item in asks:
                    offers_dict["ask"].append({"quantity": item[1], "rate": item[0]})

            return offers_dict
        else:
            raise Exception(f"Empty bids and asks list in BITBAY for ({currencies[0]},{currencies[1]})")

    def request_market_data(self):
        markets = ApiRequest.make_request(f'{self.__INFO["market_info_URL"]}')
        markets_list = []
        if markets is not None and markets["status"] == "Ok":
            for market in markets["items"].keys():
                symbols = re.split("-", market)
                markets_list.append((symbols[0], symbols[1]))
        return markets_list