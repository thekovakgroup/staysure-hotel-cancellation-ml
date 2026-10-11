"""Validated request and response schemas for the StaySure prediction API."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BookingRequest(BaseModel):
    """Reservation information available immediately after confirmation."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "hotel": "Resort Hotel",
                "lead_time": 7,
                "arrival_date_year": 2015,
                "arrival_date_month": "July",
                "arrival_date_week_number": 27,
                "arrival_date_day_of_month": 1,
                "stays_in_weekend_nights": 0,
                "stays_in_week_nights": 1,
                "adults": 1,
                "children": 0.0,
                "babies": 0,
                "meal": "BB",
                "country": "GBR",
                "market_segment": "Direct",
                "distribution_channel": "Direct",
                "is_repeated_guest": 0,
                "previous_cancellations": 0,
                "previous_bookings_not_canceled": 0,
                "reserved_room_type": "A",
                "deposit_type": "No Deposit",
                "agent": 0.0,
                "customer_type": "Transient",
                "adr": 75.0,
                "required_car_parking_spaces": 0,
                "total_of_special_requests": 0,
                "total_guests": 1.0,
                "total_nights": 1,
            }
        },
    )

    hotel: Literal["Resort Hotel", "City Hotel"]
    lead_time: int = Field(ge=0, le=1000)
    arrival_date_year: int = Field(ge=2000, le=2100)
    arrival_date_month: Literal[
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    arrival_date_week_number: int = Field(ge=1, le=53)
    arrival_date_day_of_month: int = Field(ge=1, le=31)
    stays_in_weekend_nights: int = Field(ge=0, le=30)
    stays_in_week_nights: int = Field(ge=0, le=60)
    adults: int = Field(ge=1, le=20)
    children: float = Field(ge=0, le=20)
    babies: int = Field(ge=0, le=20)
    meal: str = Field(min_length=1, max_length=32)
    country: str = Field(min_length=2, max_length=32)
    market_segment: str = Field(min_length=1, max_length=64)
    distribution_channel: str = Field(min_length=1, max_length=64)
    is_repeated_guest: Literal[0, 1]
    previous_cancellations: int = Field(ge=0)
    previous_bookings_not_canceled: int = Field(ge=0)
    reserved_room_type: str = Field(min_length=1, max_length=8)
    deposit_type: str = Field(min_length=1, max_length=32)
    agent: float = Field(ge=0)
    customer_type: str = Field(min_length=1, max_length=32)
    adr: float = Field(ge=0, le=10000)
    required_car_parking_spaces: int = Field(ge=0, le=10)
    total_of_special_requests: int = Field(ge=0, le=20)
    total_guests: float = Field(ge=1, le=60)
    total_nights: int = Field(ge=1, le=90)

    @model_validator(mode="after")
    def validate_derived_totals(self) -> "BookingRequest":
        expected_guests = float(self.adults) + self.children + float(self.babies)
        if abs(self.total_guests - expected_guests) > 1e-9:
            raise ValueError(
                "total_guests must equal adults + children + babies"
            )

        expected_nights = self.stays_in_weekend_nights + self.stays_in_week_nights
        if self.total_nights != expected_nights:
            raise ValueError(
                "total_nights must equal stays_in_weekend_nights + "
                "stays_in_week_nights"
            )
        return self


class PredictionResponse(BaseModel):
    prediction: Literal[0, 1]
    risk_label: Literal["unlikely_to_cancel", "likely_to_cancel"]
    cancellation_probability: float = Field(ge=0, le=1)
    threshold: float = Field(ge=0, le=1)
    model_name: str


class HealthResponse(BaseModel):
    status: Literal["ok"]
    model_loaded: bool
    threshold: float = Field(ge=0, le=1)
    input_features: int = Field(gt=0)
    transformed_features: int = Field(gt=0)


class ModelInfoResponse(BaseModel):
    model_name: str
    threshold: float = Field(ge=0, le=1)
    selected_params: dict[str, int | float | str | None]
    input_features: list[str]
    transformed_feature_count: int = Field(gt=0)
