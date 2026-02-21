FROM python:3.13-slim

RUN pip install uv

WORKDIR /

COPY main.py main.py
COPY ui.py ui.py
COPY uv.lock uv.lock
COPY pyproject.toml pyproject.toml
COPY README.md README.md

RUN uv sync --locked --no-cache --no-install-project

RUN uv run python -m spacy download en_core_web_lg && \
    uv run python -m spacy download en_core_web_sm && \
    uv run python -m spacy download da_core_news_lg

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]