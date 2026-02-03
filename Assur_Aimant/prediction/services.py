import joblib
from django.conf import settings
from pathlib import Path

MODEL_PATH = Path(settings.BASE_DIR) / "assur_predict" / "ml" / "gb_pipeline.joblib"
RMSE_PATH = Path(settings.BASE_DIR) / "assur_predict" / "ml" / "rmse.joblib"

model = joblib.load(MODEL_PATH)
rmse = joblib.load(RMSE_PATH)
