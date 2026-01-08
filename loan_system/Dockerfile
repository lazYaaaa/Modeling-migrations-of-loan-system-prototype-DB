FROM php:8.2-fpm

WORKDIR /var/www

COPY . .

RUN apt-get update && apt-get install -y \
    libpq-dev \
    && docker-php-ext-install pdo pdo_pgsql \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 9000

CMD ["php-fpm", "-F"]