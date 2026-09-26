FROM python:3.12-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


FROM base AS test

COPY app.py test_app.py ./

RUN pytest -q


FROM base AS runtime

RUN useradd --create-home appuser

COPY app.py ./

USER appuser

ENV APP_ENV=local
ENV APP_VERSION=dev
ENV BUILD_NUMBER=0
ENV GIT_COMMIT=unknown

EXPOSE 5000

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health')" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
