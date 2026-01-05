FROM php:8.2-cli

WORKDIR /var/www

COPY . .

RUN apt-get update && apt-get install -y \
    libpq-dev \
    && docker-php-ext-install pdo pdo_pgsql \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8000

# Запуск встроенного PHP-сервера с явным указанием документ рута
CMD ["php", "-S", "0.0.0.0:8000", "-t", "/var/www", "router.php"]