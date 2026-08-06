"""Runtime configuration for the Quiz frontend."""

import os

API_URL = os.environ.get("QUIZ_API_URL", "http://localhost:8000")
API_TIMEOUT = float(os.environ.get("QUIZ_API_TIMEOUT", "15"))
APP_TITLE = "Incluir Quiz"
