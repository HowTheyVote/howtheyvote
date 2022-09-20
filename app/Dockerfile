FROM php:8.1-alpine3.16

RUN apk --update add \
    build-base \
    autoconf \
    libressl-dev \
    libzip-dev \
    libpng-dev \
    libjpeg-turbo-dev \
    libwebp-dev \
    bash \
    less \
    make

RUN pecl install pcov && docker-php-ext-enable pcov

RUN docker-php-ext-configure gd \
    --enable-gd \
    --with-jpeg \
    --with-webp

RUN docker-php-ext-install \
    bcmath \
    ctype \
    zip \
    mysqli \
    pdo_mysql \
    gd

RUN apk add nodejs npm

COPY --from=composer/composer /usr/bin/composer /usr/bin/composer

RUN composer global require laravel/installer
RUN echo "PATH=$PATH:~/.composer/vendor/bin" >> ~/.bashrc

RUN mkdir -p /app
WORKDIR /app

COPY . .
