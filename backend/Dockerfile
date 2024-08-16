FROM python:3.12-alpine3.20

RUN apk --update add \
    build-base \
    libffi-dev \
    # TODO: Switch back to LibreSSL once conflicts on Alpine 3.17 are resolved.
    openssl-dev \
    libxml2-dev \
    libxslt-dev \
    python3-dev \
    bash \
    less \
    make \
    cargo \
    sqlite \
    tmux \
    xapian-core \
    xapian-bindings-python3

RUN pip install poetry

WORKDIR /howtheyvote/backend

# Copy dependencies required to install dependencies
COPY pyproject.toml pyproject.toml
COPY poetry.toml poetry.toml
COPY poetry.lock poetry.lock
RUN poetry env use python3.12
RUN poetry install

# Make Python packages installed via apk (e.g. xapian) available in venv
RUN echo "/usr/lib/python3.12/site-packages" > .venv/lib/python3.12/site-packages/system.pth

COPY . .

# Install again in order to make the `htv` CLI script available
RUN poetry install

ENV TZ=UTC
ENV ALEMBIC_CONFIG=./howtheyvote/alembic/alembic.ini
ENV PATH="/howtheyvote/backend/.venv/bin:$PATH"

CMD gunicorn -b [::]:5000 --workers=5 --forwarded-allow-ips=* howtheyvote.wsgi:app
