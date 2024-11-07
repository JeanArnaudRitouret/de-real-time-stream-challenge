import random
import  time
from datetime import datetime, timezone
from typing import List, Literal
import threading
from dataclasses import dataclass
from de_real_time_stream_challenge.src.config import quotes_db, update_interval_seconds
from de_real_time_stream_challenge.models.Quotes import Quote

@dataclass
class CurrencyPair:
    name: str
    mean: float
    std_dev: float


currency_pairs = [
    CurrencyPair(name='BTC-NOK', mean=820000, std_dev=5000),
    CurrencyPair(name='ETH-NOK', mean=29000, std_dev=400)
]


def get_level2_batch_message(
        type: Literal["snapshot", "l2update"] = "snapshot",
        currency_pairs: List[CurrencyPair]=currency_pairs
    ) -> List:
    level2_message = []

    for currency_pair in currency_pairs:
        bids = []
        asks = []
        # We generate a random number of bids and asks to simulate the order book feed when subscribing or after an update
        for i in range(random.randint(1, 1)):
            bid_price, bid_size, ask_price, ask_size = get_random_bid_ask_parameters(currency_pair)
            bids.append([str(bid_price), str(bid_size)])
            asks.append([str(ask_price), str(ask_size)])

        if type=='snapshot':
            level2_message.append({
                "type": type,
                "product_id": currency_pair.name,
                "bids": bids,
                "asks": asks
            })
        elif type=='l2update':
            level2_message.append({
                "type": type,
                "product_id": currency_pair.name,
                "time": str(datetime.now(timezone.utc).isoformat(timespec='microseconds')),
                "changes": [["buy", bid[0], bid[1]] for bid in bids] + [["sell", ask[0], ask[1]] for ask in asks]
            })
    return level2_message


def get_random_bid_ask_parameters(currency_pair=CurrencyPair) -> tuple[float]:
    # We generate random bid and ask prices and sizes based on the mean and standard deviation of the currency pair and a normal distribution
    bid_price = round(
        random.normalvariate(
            mu=currency_pair.mean - 2*currency_pair.std_dev,
            sigma=currency_pair.std_dev
        ),
        2 # We round the price to 2 decimals
    )
    bid_size = round(
        max(0, random.normalvariate(0.5, 0.3)),
        8 # We round the size to 8 decimals
    ) # We ensure the size is positive, 0 means that there is no order anymore
    ask_price = round(
        random.normalvariate(
            mu=currency_pair.mean + 2*currency_pair.std_dev,
            sigma=currency_pair.std_dev
        ),
        2 # We round the price to 1 decimal
    )
    ask_size = round(
        max(0, random.normalvariate(0.5, 0.3)),
        8 # We round the size to 8 decimals
    ) # We ensure the size is positive, 0 means that there is no order anymore
    return bid_price, bid_size, ask_price, ask_size


def simulate_data_stream(print_quotes: bool = False) -> None:
    global quotes_db
    cnt = 0
    while True:
        try:
            if cnt==0:
                # When "opening" the stream, we receive a snapshot of the order book, i.e. the current state
                snapshot = get_level2_batch_message(type="snapshot")
                for currency_pair_snapshot in snapshot:
                    for price, quantity in currency_pair_snapshot['bids']:
                        quote = Quote(
                            currency_pair_name=currency_pair_snapshot['product_id'],
                            side='bid',
                            price=price,
                            quantity=quantity,
                            timestamp=datetime.now()
                        )
                        quotes_db += [quote]
                    for price, quantity in currency_pair_snapshot['asks']:
                        quote = Quote(
                            currency_pair_name=currency_pair_snapshot['product_id'],
                            side='ask',
                            price=price,
                            quantity=quantity,
                            timestamp=datetime.now()
                        )
                        quotes_db += [quote]
            else:
                # After the snapshot, we receive updates to the order book
                l2update = get_level2_batch_message(type="l2update")
                for currency_pair_l2update in l2update:
                    for side, price, quantity in currency_pair_l2update['changes']:
                        quote = Quote(
                            currency_pair_name=currency_pair_l2update['product_id'],
                            side=(
                                'bid'
                                if side == 'buy'
                                else 'ask'
                            ),
                            price=price,
                            quantity=quantity,
                            timestamp=datetime.now()
                        )
                        quotes_db += [quote]
        except Exception as e:
            print(f'Error when creating a quote: {e}')
        cnt += 1

        if print_quotes:
            print(f'quotes: {quotes_db}')

        time.sleep(update_interval_seconds)


if __name__ == '__main__':
    stream_thread = threading.Thread(
        target=simulate_data_stream,
        kwargs={'print_quotes': True}
    )
    quotes_extremum_thread = threading.Thread(
        target=get_quotes_extremum,
        kwargs={'print_extremums': True, 'currency_pair_name': 'BTC-NOK'}
    )
    quotes_max_spread_thread = threading.Thread(
        target=get_quotes_max_spread,
        kwargs={'print_max_spread': True, 'currency_pair_name': 'BTC-NOK'}
    )

    stream_thread.start()
    quotes_extremum_thread.start()
    quotes_max_spread_thread.start()

    stream_thread.join()
    quotes_extremum_thread.join()
    quotes_max_spread_thread.join()
