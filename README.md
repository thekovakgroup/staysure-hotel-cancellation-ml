# StaySure ML

StaySure ML is a machine-learning project that predicts whether a hotel
reservation will be cancelled using information available when the
reservation is confirmed.

## Business Problem

Hotel cancellations make occupancy and revenue planning difficult.
This project estimates cancellation risk so hotel employees can improve
planning and prioritize reservation follow-up.

## Dataset

- Dataset: Hotel Booking Demand
- Records: 119,390
- Original columns: 32
- Target: `is_canceled`
- Task: Binary classification

The raw dataset is not included in this GitHub repository.

## Prediction Point

The prediction is made immediately after a reservation is confirmed.

## Current Status

Milestone 1: Project setup and data-audit notebook.

## Planned Models

- Dummy Classifier
- Logistic Regression
- Decision Tree
- Random Forest
- Gradient Boosting

## Project Structure

- `data/`: local datasets
- `notebooks/`: analysis and model-development notebooks
- `src/`: reusable Python code
- `tests/`: automated tests
- `models/`: saved model files
- `reports/`: charts and project reports