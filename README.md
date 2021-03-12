# EP-Votes

## Prerequisites

- Free ports 3306, 5000 and 8000.
- You’ll need `docker` and `docker-compose` for the development setup. You can find instruction on how to install Docker on the [Docker website](https://docs.docker.com/get-docker/).

## Installation

This setup is intended for development purposes only!

1. Clone this repository.
2. Run `docker-compose run app composer install` inside the cloned folder.
3. Run `docker-compose up`.

When creating a fresh development environment with a clean DB, execute `php artisan db:seed --class=GroupSeeder` and `php artisan db:seed --class=TermSeeder` inside the `app` container (e.g. with `docker-compose exec app bash` or using the command directly instead of `bash`).

---

This work is sponsored by the [Federal Ministry of Education and Research](https://bmbf.de) in the
9th round of the [Prototype Fund](https://prototypefund.de/) (Reference:
01IS21818).

<img src="./docs/logo-bmbf.svg" alt="Federal Ministry of Education and Research" height="200" />
