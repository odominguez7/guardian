# Copyright 2026 GUARDIAN — Sponsor Sustainability Agent (A2A peer #2)
#
# Deployed as a SEPARATE Cloud Run service from GUARDIAN. Same Python base,
# same uv tooling, different entrypoint.

FROM python:3.11-slim

RUN pip install --no-cache-dir uv==0.8.13

WORKDIR /code

COPY ./pyproject.toml ./README.md ./uv.lock* ./

COPY ./peers ./peers

RUN uv sync --frozen

ARG COMMIT_SHA=""
ENV COMMIT_SHA=${COMMIT_SHA}

ARG AGENT_VERSION=0.0.0
ENV AGENT_VERSION=${AGENT_VERSION}

EXPOSE 8080

CMD ["uv", "run", "uvicorn", "peers.sponsor_sustainability.fast_api_app:app", "--host", "0.0.0.0", "--port", "8080"]
