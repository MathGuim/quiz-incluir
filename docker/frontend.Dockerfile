FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app
COPY . .
RUN uv sync --frozen --package quiz-frontend

# cwd = repo root, matching render.yaml's start command shape.
# Flet serves the web UI; all backend calls happen server-side via httpx
# using QUIZ_API_URL, so the backend never needs public exposure.
CMD ["uv", "run", "flet", "run", "app/frontend/main.py", "--web", "--host", "0.0.0.0", "--port", "8080", "-vv"]
