# models/enums.py

import enum


class PaymentStatus(enum.Enum):
    prepaid = "prepaid"
    collected = "collected"
    committed = "committed"


class PaymentCurrency(enum.Enum):
    usd = "USD"
    eur = "EUR"
    inr = "INR"
    gbp = "GBP"
    jpy = "JPY"
    aud = "AUD"


class CallStatus(enum.Enum):
    uploaded = "Uploaded"
    processing = "Processing"
    processed = "Processed"
    processing_failed = "Processing Failed"
