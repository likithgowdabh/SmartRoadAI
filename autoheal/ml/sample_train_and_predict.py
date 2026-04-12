"""
Sample: train failure model on DB history, then print a prediction.

Run from the `autoheal` directory:

    python ml/sample_train_and_predict.py
"""

from __future__ import annotations

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from db.database import backend_name  # noqa: E402
from ml.failure_prediction import predict_for_machine, train_and_save_model  # noqa: E402


def main() -> None:
    print("Backend:", backend_name())
    try:
        meta = train_and_save_model()
        print("Training OK:", meta)
    except ValueError as e:
        print("Training skipped:", e)
    pred = predict_for_machine("Machine A2", current_temp=82.0, current_vib=0.65, current_volt=235.0)
    print("Prediction:", pred)


if __name__ == "__main__":
    main()
