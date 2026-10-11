"""Integration tests for the StaySure FastAPI application."""

from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from app.main import app


VALID_BOOKING = {
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


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_root(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["documentation"] == "/docs"


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["model_loaded"] is True
    assert body["threshold"] == pytest.approx(0.45)
    assert body["input_features"] == 27
    assert body["transformed_features"] == 522


def test_predict_valid_booking(client: TestClient) -> None:
    response = client.post("/predict", json=VALID_BOOKING)
    assert response.status_code == 200
    body = response.json()
    assert body["prediction"] in (0, 1)
    assert body["risk_label"] in (
        "unlikely_to_cancel",
        "likely_to_cancel",
    )
    assert 0.0 <= body["cancellation_probability"] <= 1.0
    assert body["threshold"] == pytest.approx(0.45)
    assert body["model_name"] == "random_forest_tuned"


def test_negative_lead_time_is_rejected(client: TestClient) -> None:
    payload = deepcopy(VALID_BOOKING)
    payload["lead_time"] = -1
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_inconsistent_total_nights_is_rejected(client: TestClient) -> None:
    payload = deepcopy(VALID_BOOKING)
    payload["total_nights"] = 2
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_extra_field_is_rejected(client: TestClient) -> None:
    payload = deepcopy(VALID_BOOKING)
    payload["reservation_status"] = "Canceled"
    response = client.post("/predict", json=payload)
    assert response.status_code == 422
