FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md DEV_SPEC.md ./
COPY src ./src
COPY configs ./configs
RUN python -m pip install --no-cache-dir -e .

CMD ["python", "-m", "engineering_rag.api.main"]

