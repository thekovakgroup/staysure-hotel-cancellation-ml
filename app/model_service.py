"""Loading and inference logic for the StaySure cancellation model."""

from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from app.schemas import BookingRequest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PREPROCESSOR_PATH = PROJECT_ROOT / "models" / "preprocessing_pipeline.joblib"
MODEL_BUNDLE_PATH = PROJECT_ROOT / "models" / "random_forest_tuned_bundle.joblib"


class ModelService:
    """Owns validated model artifacts and performs one-row inference."""

    model_name = "random_forest_tuned"

    def __init__(self) -> None:
        missing = [
            str(path)
            for path in (PREPROCESSOR_PATH, MODEL_BUNDLE_PATH)
            if not path.exists()
        ]
        if missing:
            raise FileNotFoundError(
                "Required model artifact(s) missing: " + ", ".join(missing)
            )

        self.preprocessor = joblib.load(PREPROCESSOR_PATH)
        bundle: dict[str, Any] = joblib.load(MODEL_BUNDLE_PATH)

        required_keys = {"model", "threshold", "selected_params", "feature_columns"}
        missing_keys = required_keys.difference(bundle)
        if missing_keys:
            raise ValueError(
                "Model bundle is missing required keys: "
                + ", ".join(sorted(missing_keys))
            )

        self.model = bundle["model"]
        self.threshold = float(bundle["threshold"])
        self.selected_params = dict(bundle["selected_params"])
        self.feature_columns = list(bundle["feature_columns"])
        self.transformed_feature_count = int(self.model.n_features_in_)

        transformed_names = self.preprocessor.get_feature_names_out()
        if len(transformed_names) != self.transformed_feature_count:
            raise ValueError(
                "Preprocessor output does not match the model feature count"
            )

    def predict(self, booking: BookingRequest) -> dict[str, Any]:
        payload = booking.model_dump()
        frame = pd.DataFrame([payload]).reindex(columns=self.feature_columns)
        transformed = self.preprocessor.transform(frame)
        probability = float(self.model.predict_proba(transformed)[0, 1])
        prediction = int(probability >= self.threshold)

        return {
            "prediction": prediction,
            "risk_label": (
                "likely_to_cancel" if prediction == 1 else "unlikely_to_cancel"
            ),
            "cancellation_probability": round(probability, 6),
            "threshold": round(self.threshold, 6),
            "model_name": self.model_name,
        }


@lru_cache(maxsize=1)
def get_model_service() -> ModelService:
    """Load model artifacts once per application process."""

    return ModelService()
