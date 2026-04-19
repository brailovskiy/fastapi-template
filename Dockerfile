FROM 3.14.4-trixie as compile-image
WORKDIR /app/

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    DOCKER_CONTAINER=1 \
    POETRY_VERSION=1.8.2

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc git ssh \
    && apt-get clean

RUN pip install poetry==$POETRY_VERSION

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.in-project true && \
    poetry config installer.max-workers 10 && \
    poetry config virtualenvs.create true && \
    poetry install --no-interaction --no-ansi -vvv && \
    rm -rf $POETRY_CACHE_DIR


FROM compile-image as production

RUN poetry install --no-interaction --no-ansi
COPY . /app
ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["uvicorn", "app.main:get_app", "--host", "0.0.0.0", "--port", "8000", "--factory"]