from datetime import datetime, timezone
import  time
from typing import List
import pandas as pd
from de_real_time_stream_challenge.src.config import quotes_db, quote_summary_db, update_interval_seconds
from de_real_time_stream_challenge.models.Quotes import QuoteSummary

def get_quotes_extremum(
        currency_pair_name: str = 'BTC-NOK',
        print_extremums: bool = False
    ) -> None:
    global quotes_db, quote_summary_db

    while True:
        if not quotes_db:
            print('No quotes available yet in get_quotes_extremum')
            time.sleep(update_interval_seconds)
            continue
        #  Convert the list of all historical quotes to a pandas DataFrame
        df_quotes = pd.DataFrame([q.__dict__ for q in quotes_db])

        df_quotes_currency_pair = df_quotes[df_quotes['currency_pair_name'] == currency_pair_name]
        if df_quotes_currency_pair.empty:
            print(f'No quotes for currency pair {currency_pair_name}')
            time.sleep(update_interval_seconds)
            continue

        # get the latest quote for each currency pair, side, and price
        df_latest_quotes = (
            df_quotes_currency_pair.sort_values(by="timestamp")
            .groupby(["currency_pair_name", "side", "price"], as_index=False)
            .last()  # Keep only the last entry in each group, which has the latest timestamp
        )
        # we remove the quotes with quantity = 0 which are quotes that have been removed from the order book
        df_latest_active_quotes = df_latest_quotes[df_latest_quotes["quantity"] != 0]


        # Calculate lowest ask and lowest bid
        lowest_ask = float(df_latest_active_quotes[df_latest_active_quotes['side']=='ask']['price'].min())
        lowest_bid = float(df_latest_active_quotes[df_latest_active_quotes['side']=='bid']['price'].min())
        # Calculate highest bid and highest ask
        highest_bid = float(df_latest_active_quotes[df_latest_active_quotes['side']=='bid']['price'].max())
        highest_ask = float(df_latest_active_quotes[df_latest_active_quotes['side']=='ask']['price'].max())
        # create a QuoteSummary object
        quote_summary = QuoteSummary(
            currency_pair_name=currency_pair_name,
            highest_ask_price=highest_ask,
            lowest_ask_price=lowest_ask,
            mid_price=(lowest_ask+highest_bid)/2,
            highest_bid_price=highest_bid,
            lowest_bid_price=lowest_bid,
            timestamp = datetime.now(timezone.utc),
        )
        quote_summary_db.append(quote_summary)

        time.sleep(update_interval_seconds)
        if print_extremums:
            print(f'For the currency pair: {currency_pair_name}')
            print(f'Lowest ask: {lowest_ask}, Highest bid: {highest_bid}')
            print(f'Highest ask: {highest_ask}, Lowest bid: {lowest_bid}')


def get_quotes_max_spread(
    currency_pair_name: str = 'BTC-NOK',
    print_max_spread: bool = False
) -> None:
    global quote_summary_db

    while True:
        df_quote_summary = pd.DataFrame([q.__dict__ for q in quote_summary_db])
        if df_quote_summary.empty:
            print('No quote summary available yet in get_quotes_max_spread')
            time.sleep(update_interval_seconds)
            continue

        # We filter the quote summary by the currency pair name and check that it is not empty
        df_quote_summary_currency_pair = df_quote_summary[df_quote_summary['currency_pair_name'] == currency_pair_name]
        if df_quote_summary_currency_pair.empty:
            print(f"No data available in get_quotes_max_spread for currency pair: {currency_pair_name}")
            time.sleep(update_interval_seconds)
            continue

        # We assume that the max spread we're interested in is calculated between highest ask and lowest bid
        df_quote_summary_currency_pair['spread'] = df_quote_summary_currency_pair['highest_ask_price'] - df_quote_summary_currency_pair['lowest_bid_price']

        time.sleep(update_interval_seconds)
        if print_max_spread:
            print(f'For the currency pair: {currency_pair_name}')
            print(f'Maximum spread: {round(df_quote_summary_currency_pair["spread"].max(), 2)}')


def predict_next_mid_price(
        currency_pair_name: str = 'BTC-NOK',
        print_next_mid_price: bool = False
    ) -> None:

    global quote_summary_db

    while True:
        if not quote_summary_db:
            print('No quote summary available yet in predict_next_mid_price')
            time.sleep(update_interval_seconds)
            continue

        # Get the latest two mid prices
        df_quote_summary = pd.DataFrame([q.__dict__ for q in quote_summary_db])

        # We filter the quote summary by the currency pair name and check that it is not empty
        df_quote_summary_currency_pair = df_quote_summary[df_quote_summary['currency_pair_name'] == currency_pair_name]
        if df_quote_summary_currency_pair.empty:
            print(f"No data available in predict_next_mid_price for currency pair: {currency_pair_name}")
            time.sleep(update_interval_seconds)
            continue

        # We calculate the moving average of the last 2 prices
        df_quote_summary_currency_pair = df_quote_summary_currency_pair.sort_values(by="timestamp", ascending=False)
        latest_mid_prices = df_quote_summary_currency_pair['mid_price'].head(2)
        if len(latest_mid_prices) == 1:
            # If there is only one mid price available, use it
            predicted_mid_price = latest_mid_prices.iloc[0]
        else:
            # Otherwise use the average of the two latest mid prices
            predicted_mid_price = latest_mid_prices.mean()

        time.sleep(update_interval_seconds)
        if print_next_mid_price:
            print(f'Predicted next mid price for currency pair {currency_pair_name}: {predicted_mid_price}')





if __name__ == '__main__':
    # quotes = [
    #     Quote(currency_pair_name='BTC-NOK', side='bid', price=815543.9149111389, quantity=0.6267406663026884, timestamp=datetime.datetime(2024, 11, 6, 18, 11, 59, 254267)),
    #     Quote(currency_pair_name='BTC-NOK', side='bid', price=815543.9149111389, quantity=0.5, timestamp=datetime.datetime(2024, 11, 6, 18, 12, 59, 254267)),
    #     Quote(currency_pair_name='BTC-NOK', side='bid', price=826016.7645705618, quantity=0.6409804365162899, timestamp=datetime.datetime(2024, 11, 6, 18, 11, 59, 254290)),
    #     Quote(currency_pair_name='BTC-NOK', side='ask', price=818471.598794355, quantity=0.6209118372142054, timestamp=datetime.datetime(2024, 11, 6, 18, 11, 59, 254292)),
    #     Quote(currency_pair_name='BTC-NOK', side='ask', price=813201.1229592981, quantity=0.6973157828359217, timestamp=datetime.datetime(2024, 11, 6, 18, 11, 59, 254294)),
    # ]
    # get_quotes_extremum(
    #     quotes_db=quotes,
    #     print_extremum=True
    # )
    pass
