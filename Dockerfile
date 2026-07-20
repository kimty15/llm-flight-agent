FROM python:3.12-slim-bookworm

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

COPY pyproject.toml README.md ./
COPY agents ./agents
COPY config ./config
COPY core ./core
COPY observability ./observability
COPY param ./param
COPY prompts ./prompts
COPY safety ./safety
COPY logger.py app.py ./

RUN pip install --no-cache-dir -e .

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
