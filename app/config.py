import os

VCR_RECORD_MODE = os.getenv("VCR_RECORD_MODE", "none")
API_BASE_URL = os.getenv("API_BASE_URL", "https://www.kaggle.com/api/v1")
