# Update this build arg whenever updating the Python base image
ARG PYTHON_VERSION=3.14
ARG XAPIAN_VERSION=2.0.0

# Base images aren't parameterized because that breaks Dependabot updates
FROM python:3.14-alpine3.24 AS builder

ARG XAPIAN_VERSION

RUN apk add --no-cache \
    build-base \
    swig \
    pkgconf \
    python3-dev \
    wget \
    xz \
    zlib-dev

WORKDIR /build

RUN wget -q https://oligarchy.co.uk/xapian/${XAPIAN_VERSION}/xapian-core-${XAPIAN_VERSION}.tar.xz \
    && tar xf xapian-core-${XAPIAN_VERSION}.tar.xz \
    && cd xapian-core-${XAPIAN_VERSION} \
    && ./configure --prefix=/usr/local \
    && make -j$(nproc) \
    && make install \
    && ldconfig /usr/local/lib

# Sphinx is used to build the Xapian docs. We don’t need the docs, but there’s no way
# to disable building the docs when building the Python bindings.
RUN pip install --no-cache-dir sphinx docutils

RUN wget -q https://oligarchy.co.uk/xapian/${XAPIAN_VERSION}/xapian-bindings-${XAPIAN_VERSION}.tar.xz \
    && tar xf xapian-bindings-${XAPIAN_VERSION}.tar.xz \
    && cd xapian-bindings-${XAPIAN_VERSION} \
    && ./configure --with-python3 PYTHON=/usr/local/bin/python3 \
    && make -j$(nproc) \
    && make install

FROM python:3.14-alpine3.24

ARG PYTHON_VERSION

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
    tmux

RUN pip install poetry

WORKDIR /howtheyvote/backend

# Copy files required to install dependencies
COPY pyproject.toml poetry.toml poetry.lock ./

RUN poetry env use python${PYTHON_VERSION}

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

# Copy Xapian and the Python bindings from the builder stage
COPY --from=builder /usr/local/lib/libxapian.so* /usr/local/lib/
COPY --from=builder /usr/local/lib/python${PYTHON_VERSION}/site-packages/xapian /usr/local/lib/python${PYTHON_VERSION}/site-packages/xapian
COPY --from=builder /usr/local/share/xapian-core/stopwords/english.list /usr/local/share/xapian-core/stopwords/english.list
RUN ldconfig /usr/local/lib

# Make Python Xapian package accessible
ENV PYTHONPATH=/usr/local/lib/python${PYTHON_VERSION}/site-packages

CMD ["gunicorn", "-b", "[::]:5000", "--workers=5", "--forwarded-allow-ips=*", "howtheyvote.wsgi:app"]
