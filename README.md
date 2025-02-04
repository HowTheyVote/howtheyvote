# HowTheyVote.eu

**[HowTheyVote.eu](https://howtheyvote.eu)** makes vote results of the European Parliament transparent and accessible – for citizens, journalists, and activists.

The European Union is one of the largest democracies in the world. The European Parliament, with its 720 members from the EU’s 27 member states, represents just over 440 million Europeans. Although the Parliament publishes information such as agendas, minutes, and vote results on its website, it can be quite difficult to find out what MEPs voted on or how a particular vote turned out. HowTheyVote.eu compiles voting data from various official sources and allows anyone to search for votes and view the results.

**[Read more about HowTheyVote.eu →](https://howtheyvote.eu/about)**

## Development environment

In order to set up a development environment on your computer please make sure you have [Docker and Docker Compose](https://docs.docker.com/engine/install/) installed on your computer.

Before you run HowTheyVote.eu locally for the first time, you will need to install dependencies for the frontend and backend:

```
docker compose run --rm frontend npm install
docker compose run --rm backend poetry install
```

Create an `.env` file according to `.env.template`.

Upgrade the system to run database migration and configure the search index:

```
docker compose run --rm backend htv system upgrade
```

Finally, you can start all required containers:

```
docker compose up -d
```

You can now access the application at `https://localhost`. Note that we use self-signed TLS certificates during development. Your browser will most likely display a certificate warning when you open the application for the first time.

At this point, there isn’t yet any data in your local database. You can use the [CLI](#cli) to run data pipelines.

> [!TIP]
> On Linux systems, due to the way Docker works by default, files created within the containers (such as the database file), will be owned by `root`.
> In order to easily work with them via your ordinary user account, you can use the solution described [here](https://stackoverflow.com/a/70613576/4418325).
> As a workaround, running `sudo chown -R $USER .` from the root directory of the project also works.           

## CLI

The `htv` CLI is installed in the `backend` container and provides a few commands that can be helpful during development. In order to run CLI commands make sure to first create a shell in the `backend` container:

```
docker compose exec backend bash
```

While we use a background worker to run data pipelines on a regular schedule in production, you can also run them manually using the CLI:

```
htv pipeline members --term=10
htv pipeline sessions --term=10
htv pipeline rcv-list --term=10 --date=2024-07-17
htv pipeline press --date=2024-07-17
```

In order to run all data pipelines for an entire term, run the following command. Please note that this command may take multiple hours to complete.

```
htv pipeline all --term=10
```

---

Parts of this work were sponsored by the Federal Ministry of Education and Research in the 9th round of the Prototype Fund in 2021 (Reference: 01IS21818). Throughout 2025, this project is supported by the MIZ Babelsberg.

<img src="./docs/funders.png" alt="Logo of the Federal Ministry of Education and Research of Germany, the Prototype Fund and the MIZ Babelsberg." height="auto" />
