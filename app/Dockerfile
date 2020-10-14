FROM php:7.4.11-alpine3.12

RUN apk --update add \
    build-base \
    libressl-dev \
    libzip-dev \
    bash \
    less \
    make \
    composer

RUN docker-php-ext-install \
    bcmath \
    ctype \
    zip \
    mysqli \
    pdo_mysql

RUN composer global require laravel/installer
RUN echo "PATH=$PATH:~/.composer/vendor/bin" >> ~/.bashrc

RUN mkdir -p /app
WORKDIR /app

COPY . .
