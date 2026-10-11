# Milestone 9 — FastAPI Model Service

## Objective

Expose the tuned StaySure hotel-cancellation model through a validated REST API that can return predictions from reservation data.

## Implementation

| Component | Purpose |
|---|---|
| `app/main.py` | Defines the FastAPI application and API routes |
| `app/schemas.py` | Validates request and response data with Pydantic |
| `app/model_service.py` | Loads the preprocessing pipeline and tuned model bundle and performs inference |
| `tests/test_api.py` | Tests endpoints, predictions, and invalid requests |
| `requirements.txt` | Records the API and testing dependencies |

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Returns basic API information |
| GET | `/health` | Confirms that the API and model artifacts loaded successfully |
| GET | `/model-info` | Returns model metadata and operating-threshold information |
| POST | `/predict` | Returns a hotel-cancellation risk prediction |

Interactive API documentation is available at `/docs` while the service is running.

## Model Contract

- Model: tuned random forest classifier
- Operating threshold: `0.45`
- Raw input features: `27`
- Transformed features: `522`
- Preprocessor: fitted scikit-learn `ColumnTransformer`
- Output: prediction, risk label, cancellation probability, threshold, and model name

## Validation Controls

The request schema:

- Requires all 27 model input fields
- Rejects unexpected fields
- Rejects invalid negative values
- Checks that `total_guests` agrees with adults, children, and babies
- Checks that `total_nights` agrees with weekday and weekend nights

These controls help prevent malformed or inconsistent reservations from reaching the model.

## Verification Results

- Automated tests: `6 passed`
- Dependency check: no broken requirements
- Health endpoint: HTTP `200`
- Model loaded: `true`
- Live prediction endpoint: HTTP `200`
- Example cancellation probability: `0.025382`
- Example prediction: `0`
- Example risk label: `Unlikely_to_cancel`

The example probability was below the frozen `0.45` operating threshold, so the reservation was classified as unlikely to cancel.

## Local Commands

Start the API:

```text
python -m uvicorn app.main:app --reload
```

Run the automated tests:

```text
python -m pytest -q
```

Open the interactive documentation:

```text
http://127.0.0.1:8000/docs
```

## Artifact Requirements

The service requires these local model artifacts:

- `models/preprocessing_pipeline.joblib`
- `models/random_forest_tuned_bundle.joblib`

The model artifacts are intentionally ignored by Git. On a new computer, they must be rebuilt by executing the project notebooks through Milestone 6 or restored from an approved model-artifact store.

## Limitations and Production Considerations

- The model was trained on historical hotel-booking data and may experience performance drift.
- Predictions are decision-support signals, not guarantees or causal conclusions.
- Production deployment should add authentication, rate limiting, structured logging, model-version tracking, monitoring, and secure artifact storage.
- Input and prediction distributions should be monitored for drift.
- Docker packaging and deployment configuration can be completed as a separate deployment milestone.
