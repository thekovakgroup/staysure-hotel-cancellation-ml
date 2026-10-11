"""StaySure hotel-cancellation prediction API."""

from contextlib import asynccontextmanager
import logging

from fastapi import Depends, FastAPI

from app.model_service import ModelService, get_model_service
from app.schemas import (
    BookingRequest,
    HealthResponse,
    ModelInfoResponse,
    PredictionResponse,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("staysure.api")


@asynccontextmanager
async def lifespan(_: FastAPI):
    service = get_model_service()
    logger.info(
        "Loaded %s with threshold %.2f and %d transformed features",
        service.model_name,
        service.threshold,
        service.transformed_feature_count,
    )
    yield
    get_model_service.cache_clear()


app = FastAPI(
    title="StaySure Hotel Cancellation API",
    description=(
        "Predicts hotel-reservation cancellation risk using information "
        "available immediately after reservation confirmation."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", tags=["service"])
def root() -> dict[str, str]:
    return {
        "service": "StaySure Hotel Cancellation API",
        "documentation": "/docs",
    }


@app.get("/health", response_model=HealthResponse, tags=["service"])
def health(
    service: ModelService = Depends(get_model_service),
) -> HealthResponse:
    return HealthResponse(
        status="ok",
        model_loaded=True,
        threshold=round(service.threshold, 6),
        input_features=len(service.feature_columns),
        transformed_features=service.transformed_feature_count,
    )


@app.get("/model-info", response_model=ModelInfoResponse, tags=["service"])
def model_info(
    service: ModelService = Depends(get_model_service),
) -> ModelInfoResponse:
    return ModelInfoResponse(
        model_name=service.model_name,
        threshold=round(service.threshold, 6),
        selected_params=service.selected_params,
        input_features=service.feature_columns,
        transformed_feature_count=service.transformed_feature_count,
    )


@app.post("/predict", response_model=PredictionResponse, tags=["prediction"])
def predict(
    booking: BookingRequest,
    service: ModelService = Depends(get_model_service),
) -> PredictionResponse:
    return PredictionResponse(**service.predict(booking))
