#!/bin/bash

# https://stackoverflow.com/a/246128
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

docker-compose exec mariadb mysqldump -u laravel -plaravel laravel > "$DIR"/dump-development.sql
