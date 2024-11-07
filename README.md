# DE Real Time Stream Challenge
The objective is to design a proof of concept for an application that ingests real-time data streams from Coinbase market feeds and provides selected insights at a defined cadence.

# How to install
Run `pip install .` to install the package

# How to run the simulation
Run `python main.py` in the terminal to start the simulation with one or many of the following arguments:
- `--print_quotes` : print the hisotircal quotes received every 5 seconds from a simulated WebSocket connection
- `--print_extremums`: print the extremums calculated every 5 seconds from the active quotes received
- `--print_max_spread`: print the max spread (between highest ask and lowest bid) calculated every 5 seconds from the active quotes received
- `--print_next_mid_price`: print the next mid-price predicted, from a moving average of the last 2 values. If only 2 value available, the predicted mid-price is this number. If no vaue avilable, no prediction is made.
- `currency_pair_name`: choose the currency pair to run calculation on. Must be one of "BTC-NOK" (default value) or "ETH-NOK"
