-- Testing database
CREATE DATABASE IF NOT EXISTS tests;
GRANT ALL PRIVILEGES ON tests.* TO 'laravel'@'%' IDENTIFIED BY 'laravel';
