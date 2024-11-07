# Plan Data Feed and Product Selection

*Describe how you would access and structure data from Coinbase’s real-time order book feeds. Explain any assumptions regarding data schema or handling of specific fields, e.g., price_level and quantity.*

- Coinbase makes accessible a WebSocket protocol which would be the most convenient in order to access real-time data from Coinbase about order book feeds, as it allows to keep a connection open and to receive updates without having to send new requests.

- Assuming that we need detailed and immediate data about specific currency pairs, we could use the level2 channel which gives an update for each change in the order book. If we could allow for a sligthly higher latency of 50 milliseconds, Coinbase recommends to use the level2_batch channel instead which delivers data in batches and allows to reduce overall traffic and limit the risks related to scalability.

- After requesting a subscription to the level2 channel, we would receive a first snapshot message, which is the state of the order book. Then we would receive l2update which are updates of the order book.

- Both message contain the field `type` (string) which is either snapshot or l2update, and the `product_ids` (string) which are currency pairs of type "BTC-USD" requested through the first subscription request.

- the snapshot message also contains the field `bids` (array) which include the current bids in the order book each cast as an array of strings `price` and `size` to preserve their precision. Their precision would depend on the currency pai selected and the value of `base_increment` (for the `size`) and `quote_increment` (for the `price`). It would be necessary to validate this data during the ingestion.

- the l2update message includes the field `changes` which is an array of arrays, each array including the `side` (string, values restricted to "buy" or "sell"), and similar `price` and `size`. The size is the updated size at the price level, and 0 indicates that the order has been removed and the price level should then be removed.l2update also includes a `time` field which is an ISO 8601 formatted datetime string.


# Create A Simulated Data Stream

*Implement a small solution that generates random bid and ask prices for a few currency pairs in a 5-second interval. This should mimic the behavior of a real-time data stream and be used to test your calculation logic.*

- Run `python main.py --print_quotes`

# Function Calculations

*Using your simulated stream, implement these basic functions to calculate values at each
interval. Highest Bid and Lowest Ask: Refresh these values at a specified interval (e.g., every 5 seconds). Max Spread: Ttrack the largest spread between bid and ask prices over time. Mid-Price and Forecasting: A basic forecasting method (e.g., moving average) for the mid-price*

- Run `python main.py --print_extremums --print_max_spread --print_next_mid_price --currency_pair_name BTC-NOK`
- Run `python main.py --print_extremums --print_max_spread --print_next_mid_price --currency_pair_name ETH-NOK`

# Error Handling and Robustness
*Explain how you’d design resilience into the application with retry mechanisms or error handling (e.g., for API outages or data inconsistencies).
Specify any edge cases you’d consider, like empty order books or malformed data, and how you would either handle or ignore them.*

- In case of an API outage, the flow of updates would be disrupted, which can result in missing updates  for a prolonged period. We could catch this issue either by monitoring error message or status codes from WebSocket indicating an issue, or by monitoring intervals without an update, for instance when we expect an update every 50 milliseconds in a level2_batch channel. We can also use the heartbeat channel to confirm the connection is still active.
- In that case we must subscribe again to the WebSocket in order to receive a clean state of the order book, or we risk missing an update. We might implement a reconnecting strategy like exponential backoff in order to not overwhelm the API with reconnection attempts. Finally, we might want to implement a failsafe in the form of a REST API in case we are unsuccessful in reconnecting to the WebSocket for a prolonged period.
- Coinbase recommends to run at least one instance per currency pair. If this real-time data is critical to operations, we could also run multiple instances of WebSocket Clients for each pair to achieve redundancy. This would howver requires deuplication in the processing and increased resources.
- In order to manage data inconsistencies, we want to validate the data correctness of each message received during the parsing, by validating the type of each field received, checking that their range is within reasonable bounds and that values are correct (e.g cfor a currency pair), that mandatory fields are populated and catching errors at different steps with try-except mechanisms.
- In the case of an empty order book, either in the snapshot or update, this signals an issue and I would revert to open a new connection to get a new snapshot, with an exponential retry mechanism too. We might also want to use a REST API failsafe in case of a prolonged period with only empty order books received.
- We should also implement tests to monitor the health of data stored into the database (e.g non null values, uniqueness of timestamp at a cetain level, max spread being historically within bounds) and the health of our integration (using mock data and clean database, checking that the results are as expected).


# Documentation and Assumptions
*Summarize the primary assumptions you’re making about the API data and any design choices you’d highlight to stakeholders.*
- I'd highlight that the data is received by batches, which is not exactly live updates but close enough for most purposes.
- I would also highlight that the data is parsed into historical quotes, which allows us to keep a record of all quotes if we were to need it in the future. However for an easier analytical purpose, these historical quotes are transformed into objects called quotes summary. Quotes summary are a "snapshot" of quotes for a currency pair at any time, with the lowest ask, highest bid and mid price.
- I would highlight clearly to stakeholders how the max spread is calculated (difference between highest ask and lowest bid) and how the next mid price is predicted (moving avereage of last 2 values)
- I have assumed that all calculations always happen in the background once the simulation starts, the user only has control on printing the results.
- I have assumed that we are interested in a simulation and not in collecting the insights. Hence I have not created a database for this simulation, instead storing temporary data into global variables in order to simplify the application. Also calculating functions don't return values that could be collected outside of thie simulation for the same reason.
- I have assumed for this simulation that no empty order books are sent either in snapshot or updates for the saeke of this simulation.
- I have assumed that we only are interested in 2 currency pairs BTC-NOK and ETH-NOK. These pairs have a price precision of 2 decimals and quantity precision of 8 decimals.
- I have assumed for this simulation that no inconsistent data is sent from the API, such as negative quantities or wrongly formatted price values or incorrect currency pairs.
- I have assumed for this simulation that all currency pairs are requested in one request, and that one message is received containing all currency pairs. The documentation mentions that one message per currency pair would actually be received.
- I have assumed that no test is need for this simulation wrt the data ingestion pipeline, the data storage and calculations.
- I have assumed that no retry mechanism is needed for this simulation.