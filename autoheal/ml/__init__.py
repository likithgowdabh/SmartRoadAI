"""ML utilities for AutoHeal AI (failure risk from historical telemetry)."""

from ml.failure_prediction import predict_for_machine, train_and_save_model

__all__ = ["predict_for_machine", "train_and_save_model"]
