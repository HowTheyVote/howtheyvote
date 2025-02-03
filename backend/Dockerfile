FROM python:3.13-alpine3.21

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

# Copy files required to install dependencies
COPY pyproject.toml poetry.toml poetry.lock .

RUN poetry env use python3.13

# Install only dependencies, but not the package itself (because that
# would fail because we haven't yet copied the code at this point)
RUN poetry install --no-root

COPY . .

# Install again in order to make the `htv` CLI script available, this
# time without the dependencies (which have been installed before)
RUN poetry install --only-root

ENV TZ=UTC
ENV ALEMBIC_CONFIG=./howtheyvote/alembic/alembic.ini
ENV PATH="/howtheyvote/backend/.venv/bin:$PATH"

# Make Python system packages (such as Xapian) accessible. This has to be the same
# as the Python version that can be installed via the Alpine package manager. At
# the time of writing, this is 3.13 on Alpine 3.21.
ENV PYTHONPATH=/usr/lib/python3.13/site-packages

CMD gunicorn -b [::]:5000 --workers=5 --forwarded-allow-ips=* howtheyvote.wsgi:app
