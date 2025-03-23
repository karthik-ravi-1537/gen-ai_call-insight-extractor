# models/enums.py

import enum


class PaymentStatus(enum.Enum):
    PREPAID = "Prepaid"
    COLLECTED = "Collected"
    COMMITTED = "Committed"
    PENDING = "Pending"

    @classmethod
    def from_string(cls, value_string: str) -> "PaymentStatus":
        """Get enum value from display string like 'Collected'"""
        for item in cls:
            if item.value == value_string:
                return item
        return cls.PENDING


class PaymentCurrency(enum.Enum):
    USD = "USD"  # Primary Currency
    INR = "INR"  # Other Currencies for Testing
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    AUD = "AUD"
    OTHER = "Other"

    @classmethod
    def from_string(cls, value_string: str) -> "PaymentCurrency":
        """Get enum value from display string like 'USD'"""
        for item in cls:
            if item.value == value_string:
                return item
        return cls.USD


class CallStatus(enum.Enum):
    UPLOADED = "Uploaded"
    PROCESSING = "Processing"
    PROCESSED = "Processed"
    PROCESSING_FAILED = "Processing Failed"

    @classmethod
    def from_string(cls, value_string: str) -> "CallStatus":
        """Get enum value from display string like 'Processing'"""
        for item in cls:
            if item.value == value_string:
                return item
        return cls.UPLOADED


class PaymentMethod(enum.Enum):
    CREDIT_CARD = "Credit Card"
    DEBIT_CARD = "Debit Card"
    ACH = "ACH"
    CHECK = "Check"
    CASH = "Cash"
    WIRE_TRANSFER = "Wire Transfer"
    OTHER = "Other"

    @classmethod
    def from_string(cls, value_string: str) -> "PaymentMethod":
        """Get enum value from display string like 'Credit Card'"""
        for item in cls:
            if item.value == value_string:
                return item
        return cls.CASH
