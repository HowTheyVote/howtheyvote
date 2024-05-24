# Architecture

HowTheyVote consists of a backend and a frontend. The backend is written in Python and does most of the work, including scraping data, reading and writing from and to the database, and providing an HTTP API. The frontend is a Node.js application that serves as a thin presentation layer, loading data from the API and returning HTML.

While strictly separating backend and frontend and allowing them to communicate only via an API causes some overhead, HowTheyVote aims to provide all of its data in a machine readable form. We initially used a more monolithic approach and exposed only some core data via an API, but ended up realizing that we want to provide a more powerful API to make it easier to reuse data from HowTheyVote.

## Backend

The backend uses the following tech stack:

* **requests**, **BeautifulSoup**, and **lxml** to parse and scrape data.
* **SQLAlchemy 2** and **Alembic** for ORM and database migrations.
* **SQLite 3** as the primary database.
* **Flask** for our API and admin interface.
* **Pytest** and **mypy** for testing and static type-checking.
* **OpenAPI** to document the API

### Scrapers

HowTheyVote scrapes and merges data about votes, plenary sessions, and the Members of the European Parliament (MEPs) from multiple official websites and publications of the European Parliament (EP).

For example, we scrape the followings sources to get information about MEPs:

* The [full list of MEPs](https://www.europarl.europa.eu/meps/en/directory/xml?leg=9) in XML format for every legislature
* The [MEP profiles](https://www.europarl.europa.eu/meps/en/96734/SKA_KELLER/home) for basic information about each MEP such as country, date of birth
* The [history of parliamentary service](https://www.europarl.europa.eu/meps/en/96734/SKA_KELLER/history/9) to get start and end dates of parliamentary service and group memberships for each MEP.

The `howtheyvote.scrapers.members` module has a scraper for each of the above sources. All scrapers are stateless[^stateless], i.e. they only depend on input parameters (this could be a parliamentary legislature or an MEP’s ID). This makes scrapers easy to test and debug. Based on these input parameters, scrapers request one or more HTML, XML, or JSON documents and extract structured data.

[^stateless]: There is a single non-stateless detail: We use a simple in-memory response cache. This is to avoid duplicate requests to the same resources. For example, the `OeilTitleScraper` in `howtheyvote.scrapers.votes` extracts a human-readable title for a vote based on information about the respective legislative procedure from the Legislative Observatory. As in many cases there will be multiple votes related to the same legislative procedure, requesting this information over and over again for every vote would be wasteful and slow.

The extracted data is stored in [fragments](./fragments.md) and is later merged into a single records per MEP.

### Analyzers

### Pipelines

## Frontend

The frontend uses the following tech stack:

* **tinyhttp** as a very simple, zero-dependency Node.js framework, primarily used for routing.
* **Preact** to define UI components. We server-render all pages, but implement a very simply variant of the islands architecture/partial hydration to enable a few interactive UI components.
* **Preact Testing Library** and the native Node.js test runner.
* **TypeScript** for static type-checking (with auto-generated types based on the OpenAPI specification).

### Islands


### CSS

We don’t use a CSS preprocessor and instead rely on many modern CSS features, e.g. CSS custom properties.

We try to stick to the [BEM naming convention](https://getbem.com/) (with the exception of a few global and helper/utility styles). Every component has a sidecar CSS file that defines styles for this component. For example, the `Button` component in `src/components/Button.tsx` imports styles from `src/components/Button.css`.
