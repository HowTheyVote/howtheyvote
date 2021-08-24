FROM python:3.8-alpine3.12

RUN apk --update add \
    build-base \
    libressl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt-dev \
    python3-dev \
    bash \
    less \
    make \
    cargo

RUN pip3 install poetry

RUN mkdir -p /app
WORKDIR /app

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock
RUN poetry env use python
RUN poetry install

COPY . .
