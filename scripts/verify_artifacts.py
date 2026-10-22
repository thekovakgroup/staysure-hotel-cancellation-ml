"""Verify deployment model artifacts against the committed manifest."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = PROJECT_ROOT / "models"
MANIFEST_PATH = MODEL_DIR / "artifact_manifest.csv"


def calculate_sha256(path: Path) -> str:
    """Return the SHA-256 digest for a file without loading it all into memory."""
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def verify_artifacts() -> int:
    """Validate every artifact listed in the deployment manifest."""
    if not MANIFEST_PATH.is_file():
        raise FileNotFoundError(f"Artifact manifest not found: {MANIFEST_PATH}")

    with MANIFEST_PATH.open(
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as manifest_file:
        rows = list(csv.DictReader(manifest_file))

    if not rows:
        raise ValueError("Artifact manifest is empty")

    failures: list[str] = []

    for row in rows:
        artifact_name = row["artifact"]
        expected_hash = row["sha256"].lower()
        expected_size = int(row["size_bytes"])
        artifact_path = MODEL_DIR / artifact_name

        if not artifact_path.is_file():
            failures.append(f"{artifact_name}: file is missing")
            continue

        actual_size = artifact_path.stat().st_size
        actual_hash = calculate_sha256(artifact_path)

        if actual_size != expected_size:
            failures.append(
                f"{artifact_name}: expected {expected_size} bytes, "
                f"found {actual_size}"
            )

        if actual_hash != expected_hash:
            failures.append(
                f"{artifact_name}: SHA-256 does not match the manifest"
            )

    if failures:
        raise RuntimeError(
            "Artifact verification failed:\n- " + "\n- ".join(failures)
        )

    return len(rows)


if __name__ == "__main__":
    verified_count = verify_artifacts()
    relative_manifest = MANIFEST_PATH.relative_to(PROJECT_ROOT)
    print(
        f"Verified {verified_count} model artifacts "
        f"against {relative_manifest}."
    )