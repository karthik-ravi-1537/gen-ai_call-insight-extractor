# models/enums.py

import enum


class PaymentStatus(enum.Enum):
    PREPAID = "Prepaid"
    COLLECTED = "Collected"
    COMMITTED = "Committed"
    PENDING = "Pending"


class PaymentCurrency(enum.Enum):
    USD = "USD"  # Primary Currency
    INR = "INR"  # Other Currencies for Testing
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    AUD = "AUD"
    OTHER = "Other"


class CallStatus(enum.Enum):
    UPLOADED = "Uploaded"
    PROCESSING = "Processing"
    PROCESSED = "Processed"
    PROCESSING_FAILED = "Processing Failed"


class PaymentMethod(enum.Enum):
    CREDIT_CARD = "Credit Card"
    DEBIT_CARD = "Debit Card"
    ACH = "ACH"
    CHECK = "Check"
    CASH = "Cash"
    WIRE_TRANSFER = "Wire Transfer"
    OTHER = "Other"
