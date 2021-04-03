# EP-Votes

## Development Setup

We use Docker for our development setup. This setup is intended for development purposes only!

1. Make sure ports 3306, 5000 and 8000 are free.
2. Install `docker` and `docker-compose`. You can find instruction on how to install Docker on the [Docker website](https://docs.docker.com/get-docker/).
3. Run `docker-compose run app composer install` inside the cloned folder.
4. Run `docker-compose up`.
5. Create `.env` files based on `scrapers/.env.example` and `app/.env.example`.
6. When creating a fresh development environment with a clean DB, execute `php artisan migrate`, `php artisan db:seed --class=GroupSeeder`, and `php artisan db:seed --class=TermSeeder` inside the `app` container (e.g. with `docker-compose exec`).

## Production Deployment

We’re using [Ansible](https://ansible.org) to manage server provisioning and deployment to production environments. Currently, the Ansible playbook `ansible/site.yml` supports deploying EP-Votes to a fresh [Uberspace 7](https://uberspace.de) account.

1. Install Ansible 2.10 or later. Update `ansible/hosts` and the respective host variables.
2. Run `ansible-playbook -i ansible/hosts --ask-vault-pass ansible/site.yml`.

---

This work is sponsored by the [Federal Ministry of Education and Research](https://bmbf.de) in the 9th round of the [Prototype Fund](https://prototypefund.de/) (Reference: 01IS21818).

<img src="./docs/logo-bmbf.svg" alt="Federal Ministry of Education and Research" height="200" />
