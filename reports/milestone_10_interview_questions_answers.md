# Milestone 10 — Interview Questions and Answers

## 1. Why containerize a machine-learning API?

Containerization packages the application code, runtime, dependencies, and model artifacts into a consistent execution environment. It reduces differences between development, CI, and production and makes the service easier to test and deploy repeatedly.

## 2. Why use a slim Python base image?

A slim image contains fewer operating-system packages than a full distribution. This reduces image size, download time, build surface, and the number of packages that may contain vulnerabilities. The tradeoff is that native build tools must be added explicitly if a dependency needs compilation.

## 3. Why copy and install the requirements file before copying the application code?

Docker caches image layers. Dependency installation changes less often than application code, so copying the requirements file first lets Docker reuse the dependency layer during later builds. That makes builds faster and more efficient.

## 4. Why separate production and test requirements?

The production container needs only the packages required to serve predictions. Test tools are necessary in CI but not at runtime. Keeping them separate reduces the production dependency surface and makes each environment’s purpose explicit.

## 5. Why pin dependency versions?

Pinned versions improve reproducibility by ensuring local development, CI, and container builds resolve the same package versions. Without pins, a future package release could change behavior or break compatibility even when the project code has not changed.

## 6. What is the purpose of `.dockerignore`?

`.dockerignore` prevents unnecessary or sensitive files from being sent to the Docker build context. In this project it excludes datasets, notebooks, reports, tests, caches, virtual environments, Git metadata, and unused models. This reduces build time and avoids accidentally embedding local files in the image.

## 7. Why run the container as a non-root user?

If an attacker exploits the application, a non-root process has fewer privileges inside the container. This follows the principle of least privilege and limits the potential impact of a compromise.

## 8. What does the Docker health check verify?

The health check calls the FastAPI `/health` endpoint. Because application startup eagerly loads and validates the model service, a successful health response indicates that the API process is running and the required model artifacts were loaded successfully.

## 9. How is artifact integrity verified?

The project stores the expected filename, byte size, and SHA-256 digest for each production artifact in `models/artifact_manifest.csv`. The verification script recalculates each size and digest and fails if a file is missing or altered.

## 10. Why is a cryptographic hash useful for model artifacts?

A cryptographic hash acts as a deterministic fingerprint. Even a small change to an artifact produces a different SHA-256 digest. This helps detect corruption, accidental replacement, or an unexpected model version before the service starts.

## 11. Are joblib or pickle model files safe to load from any source?

No. Joblib and pickle files can execute code while being deserialized. The service should load only trusted artifacts produced and controlled by the project. The hash check verifies identity and integrity, but it does not make an untrusted serialized file safe.

## 12. Why does CI run Python validation before the container job?

Unit and integration tests are faster and usually provide clearer failure messages than a container build. The container job depends on Python validation, so CI stops early when the application, dependencies, tests, or artifacts are already invalid.

## 13. What is the difference between an API test and a container smoke test?

API tests validate endpoint behavior within the Python test environment. The container smoke test validates packaging and runtime integration: the image must build, the process must start, the port must be reachable, the model must load, and `/health` must respond successfully.

## 14. Why was GitHub Actions used for Docker validation?

The older development laptop does not have Docker and does not currently have firmware virtualization enabled. GitHub Actions provides a clean Linux runner with Docker support, allowing the image to be built and tested without placing additional load on the laptop.

## 15. Why use one Uvicorn worker?

Each worker would load its own copy of the preprocessor and random forest into memory. One worker keeps memory usage predictable for this capstone and is appropriate for the expected demonstration workload. Production scaling can add instances after measuring latency, throughput, and memory use.

## 16. Why commit the two production artifacts but not every saved model?

The API needs only the fitted preprocessor and tuned-model bundle. Including baseline and candidate models would increase repository and image size without serving the production prediction path. A mature system would normally store versioned artifacts in object storage or a model registry.

## 17. Why does the workflow use read-only repository permissions?

The validation workflow only needs to read source files. Read-only permissions reduce the damage possible if a workflow step or third-party action is compromised.

## 18. Why does the workflow build but not push the image?

Milestone 10 proves that the image is buildable and operational. Publishing requires a registry, credentials or federated identity, naming and tagging rules, and a deployment decision. Keeping publishing out of this milestone avoids accidental cloud changes or charges.

## 19. What remains before AWS deployment?

The next stage must select the AWS runtime, define the region and budget, create least-privilege IAM access, create an ECR repository, establish secure GitHub-to-AWS authentication, publish a tagged image, deploy it, configure public access and logging, and verify the live endpoints.

## 20. What does Milestone 10 demonstrate to an employer?

It demonstrates that the project extends beyond notebook modeling. The model has a defined inference contract, tested API, pinned runtime, verified artifacts, least-privilege container, health checks, and automated CI that proves the container works on a clean machine.
