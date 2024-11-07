import threading
import argparse
from de_real_time_stream_challenge.src.real_time_stream_simulator import (
    simulate_data_stream
)
from de_real_time_stream_challenge.src.real_time_insights import (
    get_quotes_extremum,
    get_quotes_max_spread,
    predict_next_mid_price
)

def main(
        print_quotes:bool = False,
        print_extremums: bool = False,
        print_max_spread: bool = False,
        print_next_mid_price: bool = False,
        currency_pair_name: str = 'BTC-NOK'
):
    stream_thread = threading.Thread(
        target=simulate_data_stream,
        kwargs={'print_quotes': print_quotes}
    )
    quotes_extremum_thread = threading.Thread(
        target=get_quotes_extremum,
        kwargs={'print_extremums': print_extremums, 'currency_pair_name': currency_pair_name}
    )
    quotes_max_spread_thread = threading.Thread(
        target=get_quotes_max_spread,
        kwargs={'print_max_spread': print_max_spread, 'currency_pair_name': currency_pair_name}
    )
    predict_next_mid_price_thread = threading.Thread(
        target=predict_next_mid_price,
        kwargs={'print_next_mid_price': print_next_mid_price, 'currency_pair_name': currency_pair_name}
    )

    # Start threads
    stream_thread.start()
    quotes_extremum_thread.start()
    quotes_max_spread_thread.start()
    predict_next_mid_price_thread.start()

    # Wait for threads to complete
    stream_thread.join()
    quotes_extremum_thread.join()
    quotes_max_spread_thread.join()
    predict_next_mid_price_thread.join()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the data streaming application with options.")
    parser.add_argument('--print_quotes', action='store_true', help="Enable printing quotes from the currency pairs as they are received from the API")
    parser.add_argument('--print_extremums', action='store_true', help="Enable printing extremums as they are calculated.")
    parser.add_argument('--print_max_spread', action='store_true', help="Enable printing max spread as they are calculated")
    parser.add_argument('--print_next_mid_price', action='store_true', help="Enable printing the next mid price as it is predicted")
    parser.add_argument('--currency_pair_name', type=str, default="BTC-NOK", help="The name of the currency pair on which to run calculations, with format BTC-NOK or ETH-NOK")
    args = parser.parse_args()

    main(
        print_quotes=args.print_quotes,
        print_extremums=args.print_extremums,
        print_max_spread=args.print_max_spread,
        print_next_mid_price=args.print_next_mid_price,
        currency_pair_name=args.currency_pair_name
    )

