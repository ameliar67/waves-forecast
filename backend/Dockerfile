ARG PYTHON_VERSION="3.12-slim"
ARG POETRY_VERSION="2.1.3"

FROM python:${PYTHON_VERSION} AS build

WORKDIR /app

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1

ARG POETRY_VERSION
RUN pip install poetry==${POETRY_VERSION}

COPY pyproject.toml poetry.lock ./
RUN poetry install --without dev --no-cache --no-root && \
    pip uninstall -y poetry


FROM python:${PYTHON_VERSION} AS runtime

WORKDIR /app
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=build ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY . .

ENTRYPOINT ["python", "-m", "main"]
