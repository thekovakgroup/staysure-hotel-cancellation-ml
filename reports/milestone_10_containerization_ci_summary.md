# Milestone 10 — Containerization and Continuous Integration

## Status

Completed on October 22, 2026.

Milestone 10 packaged the StaySure FastAPI inference service as a reproducible container and introduced automated validation through GitHub Actions. No AWS resources were created and no application was deployed publicly.

## Objectives

- Separate API runtime dependencies from notebook and development dependencies.
- Package the FastAPI service and production model artifacts in a Docker image.
- Verify model artifacts using recorded file sizes and SHA-256 hashes.
- Run API tests automatically on every relevant push and pull request.
- Build and smoke-test the container remotely because Docker is unavailable on the development laptop.
- Prepare the project for a future AWS deployment without provisioning cloud resources.

## Production Service

The container serves the FastAPI application through Uvicorn on port `8000`.

Available endpoints:

- `GET /` — service metadata and documentation location
- `GET /health` — application and model-readiness status
- `GET /model-info` — model threshold, parameters, and feature contract
- `POST /predict` — hotel-cancellation risk prediction

The production inference contract remains:

- Model: tuned random forest classifier
- Operating threshold: `0.45`
- Raw input features: `27`
- Transformed model features: `522`
- Preprocessor: fitted scikit-learn `ColumnTransformer`

## Container Design

The `Dockerfile`:

- Uses Python 3.11 on Debian Bookworm Slim.
- Installs only the pinned API runtime dependencies.
- Copies only the application, verification script, and required model artifacts.
- Verifies artifact integrity during the image build.
- Runs the application as a non-root user.
- Exposes port `8000`.
- Includes a Docker health check against `/health`.
- Starts one Uvicorn worker to avoid duplicating the model in memory.

The `.dockerignore` file excludes datasets, notebooks, reports, tests, caches, local environments, Git metadata, and unused model files from the image build context.

## Dependency Separation

Three dependency roles are now defined:

- `requirements.txt` — full analysis and notebook environment
- `requirements-api.txt` — pinned production API dependencies
- `requirements-test.txt` — production dependencies plus test tooling

This separation reduces the container image scope and improves reproducibility.

## Model Artifact Integrity

The following production artifacts are included:

- `models/preprocessing_pipeline.joblib`
- `models/random_forest_tuned_bundle.joblib`

Their expected sizes and SHA-256 hashes are stored in `models/artifact_manifest.csv`.

The script `scripts/verify_artifacts.py` checks every artifact against that manifest. Verification runs locally, during the Docker build, and in GitHub Actions.

Local result:

```text
Verified 2 model artifacts against models\artifact_manifest.csv.
```

## Continuous Integration

The workflow `.github/workflows/ci.yml` runs for:

- Pushes to `main`
- Pushes to `milestone-*` branches
- Pull requests targeting `main`
- Manual workflow dispatches

### Python validation job

The first job:

1. Checks out the repository.
2. Sets up Python 3.11.9.
3. Installs `requirements-test.txt`.
4. Verifies production model artifacts.
5. Checks dependency consistency.
6. Runs the API test suite.

### Container validation job

After Python validation succeeds, the second job:

1. Configures Docker Buildx.
2. Builds the StaySure container image.
3. Starts the container on port `8000`.
4. Polls `/health` until the API becomes ready.
5. Displays the Docker health state.
6. Captures logs and removes the test container.

The workflow builds the image for validation but does not publish it to a registry.

## Validation Evidence

Local validation:

- Artifact verification: passed
- Dependency consistency: passed
- API tests: `6 passed`
- Test duration on the development laptop: `77.57 seconds`

GitHub Actions validation:

- Workflow: `StaySure CI`
- Commit: `9c36265`
- Branch: `milestone-10-containerization-ci`
- Result: passed
- Duration: `1 minute 57 seconds`

The successful workflow confirms that a clean Linux runner can reproduce the Python environment, validate the artifacts, run the tests, build the Docker image, start the container, and receive a successful health response.

## Security and Reliability Controls

- The application runs as a non-root container user.
- GitHub Actions receives read-only repository permissions.
- Checkout credentials are not persisted.
- API and test dependencies are version-pinned.
- Model artifacts are protected by SHA-256 verification.
- The health endpoint verifies that the model service loaded successfully.
- No credentials, AWS keys, or environment-secret files are committed.
- CI concurrency cancels obsolete runs for the same Git reference.

## Known Limitations

- The production model artifacts are stored in Git for this capstone. A larger production system would normally use object storage or a model registry.
- The image is validated but not yet published to a container registry.
- Authentication, rate limiting, HTTPS termination, and production monitoring are not yet configured.
- The current API performs synchronous single-record inference.
- The development laptop cannot run Docker locally, so GitHub Actions provides the independent container validation environment.

## Deployment Boundary

Milestone 10 stops before deployment. The following actions have not occurred:

- No AWS account configuration was changed.
- No IAM roles or policies were created.
- No Amazon ECR repository was created.
- No container image was pushed to a registry.
- No AWS App Runner, ECS, EC2, or load-balancer resource was created.
- No public API endpoint was launched.

The project is deployment-ready, but cloud provisioning remains a separate, explicitly controlled milestone.
