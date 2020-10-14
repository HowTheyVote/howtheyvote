FROM python:3.9.0-alpine3.12

RUN apk --update add \
    build-base \
    libressl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt-dev \
    python3-dev \
    bash \
    less \
    make

RUN pip3 install poetry

RUN mkdir -p /app
WORKDIR /app

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock
RUN poetry install

COPY . .
