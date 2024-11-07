from pydantic import BaseModel, Field, field_validator
from typing import List, Literal, Optional
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime

class Quote(BaseModel):
    currency_pair_name: str
    side: Literal["bid", "ask"]
    price: float
    quantity: float
    timestamp: datetime

    @field_validator('price', mode='before')
    def precision_to_two_decimals(cls, v):
        return float(Decimal(v).quantize(Decimal('0.00')))

    @field_validator('quantity', mode='before')
    def precision_to_8_decimals(cls, v):
        return float(Decimal(v).quantize(Decimal('0.00000000')))


class QuoteSummary(BaseModel):
    currency_pair_name: str
    highest_ask_price: float
    lowest_ask_price: float
    mid_price: float
    highest_bid_price: float
    lowest_bid_price: float
    timestamp: datetime

    @field_validator('highest_ask_price', 'lowest_ask_price', 'mid_price', 'highest_bid_price', 'lowest_bid_price', mode='before')
    def precision_to_two_decimals(cls, v):
        # Convert to Decimal, round to 2 decimal places, and cast back to float
        return float(Decimal(v).quantize(Decimal('0.00')))