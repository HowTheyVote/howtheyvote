FROM php:8-alpine3.12

RUN apk --update add \
    build-base \
    autoconf \
    libressl-dev \
    libzip-dev \
    bash \
    less \
    make \
    composer

RUN pecl install pcov && docker-php-ext-enable pcov
RUN docker-php-ext-enable pcov

RUN docker-php-ext-install \
    bcmath \
    ctype \
    zip \
    mysqli \
    pdo_mysql

RUN apk add nodejs npm

RUN composer global require laravel/installer
RUN echo "PATH=$PATH:~/.composer/vendor/bin" >> ~/.bashrc

RUN mkdir -p /app
WORKDIR /app

COPY . .
