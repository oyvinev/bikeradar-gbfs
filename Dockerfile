FROM python:3.11.5-slim-bookworm

# Do not write .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# Do not ever buffer console output
ENV PYTHONUNBUFFERED 1

RUN pip install --disable-pip-version-check poetry
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-root -v --no-interaction --no-ansi
COPY . /app

ENTRYPOINT [ "sleep", "infinity" ]

