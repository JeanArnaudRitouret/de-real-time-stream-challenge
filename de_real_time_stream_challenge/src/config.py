from typing import List
from de_real_time_stream_challenge.models.Quotes import Quote, QuoteSummary

update_interval_seconds = 5
quotes_db: List[Quote] = []
quote_summary_db: List[QuoteSummary] = []
lowest_ask: float = 0
highest_bid: float = 0