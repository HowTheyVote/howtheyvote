# Fragments

We have a couple of requirements with regards to storing scraped data:

* We need to track data provenance, i.e. we want to know when and from which source we got a specific piece of information.
* We need to be able to manually override data, for example in case there are errors in the source data or when our scrapers are not able to extract all data in a fully automated way. For example, we have occasionally seen typos in the data published by the EP.
* We need to be able to easily rerun specific scrapers for all or only some records, while retaining data extracted by other 
scrapers.
* We need to be able to merge data from multiple sources into a single record.

In order to satisfy these requirements, we use an architeture inspired by [followthemoney-store](https://github.com/alephdata/followthemoney-store). We store data extracted from data sources as separate fragments in the database. Each fragments contains some metadata and the extracted data.

The schema of the `fragment` table in our database looks like this:

| Column | Description |
| --- | --- |
|`model` | The model or type of record this fragment corresponds to. For example, this could be a fragment for a `Member` record or a `Vote` record. |
| `source_name` | A unique name of the source, in most cases this will be the name of the scraper, for example `MembersGroupsScraper` |
| `source_id` | A unique ID for the record in the source data. |
| `source_url` | The URL of the source document. |
| `timestamp` | The time when the fragment was created or updated. |
| `group_key` | A key that is used to group and merge fragments from multiple sources. |
| `data` | A JSON blob with structured data. |

After running all scrapers, we might end up with the following fragments for Ska Keller, the co-chair of the Greens/EFA group in the EP:

| model | source_name | source_id | source_url | timestamp | group_key | data |
| --- | --- | --- | --- | --- | --- | --- |
| Member | MembersScraper | 96734:8 | https://www.europarl.europa.eu/meps/en/directory/xml/?leg=8 | 2023-03-11 19:01:40 | 96734 | <pre lang="json">{"term": 8}</pre> |
| Member | MembersScraper | 96734:9 | https://www.europarl.europa.eu/meps/en/directory/xml/?leg=9 | 2023-03-11 18:51:46 | 96734 | <pre lang="json">{"term": 9}</pre> |
| Member | MemberInfoScraper | 96734 | https://www.europarl.europa.eu/meps/en/96734/NAME/home | 2023-03-11 19:18:37 | 96734 | <pre lang="json">{"email": "franziska.keller@europarl.europa.eu", "country": "DE", "twitter": "https://twitter.com/SkaKeller", "facebook": null, "last_name": "KELLER", "first_name": "Ska", "date_of_birth": "1981-11-22"}</pre> |
| Member | MemberGroupsScraper | 96734:8 | https://www.europarl.europa.eu/meps/en/96734/NAME/history/8 | 2023-03-14 19:36:44 | 96734 | <pre lang="json">{"group_memberships": [{"term": 8, "group": "GREENS", "end_date": "2016-12-13", "start_date": "2014-07-01"}, {"term": 8, "group": "GREENS", "end_date": "2019-07-01", "start_date": "2016-12-14"}]}</pre> |
| Member | MemberGroupsScraper | 96734:9 | https://www.europarl.europa.eu/meps/en/96734/NAME/history/9 | 2023-03-14 17:03:49 | 96734 | <pre lang="json">{"group_memberships": [{"term": 9, "group": "GREENS", "end_date": "2022-09-13", "start_date": "2019-07-02"}, {"term": 9, "group": "GREENS", "end_date": null, "start_date": "2022-09-14"}]}</pre> |

`96734` is the Ska Keller’s ID as assigned by the Parliament’s MEP directory. Note how some of the fragments specify a composite `source_id`. Ska Keller has been an MEP during the 8th and 9th legislatures and we use the `MemberGroupsScraper` to scrape Keller’s group memberships during each of these legislatures. `model`, `source_name`, and `source_id` uniquely identify a fragment, so in this case we need to use a `source_id` composed of the MEP ID and the legislature.

## Aggregating fragments
Because fragments store all data in a single JSON column, working directly with them would be complex and inefficient. To be able to query data more easily, we merge all fragments with the same `model` and `group_key` into a single record. The merged record is stored in a separate database table that uses a (mostly) normalized relational schema. We call this process of merging fragments *Aggregation*.

For example, all the fragments related to Ska Keller would be merged into a single record in the `members` table:

| id | first_name | last_name | country | terms | group_memberships | date_of_birth | email | facebook | twitter |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 96734 | Ska | KELLER | DE | {9,8} | <pre lang="json">[{"term": 9, "group": "GREENS", "end_date": "2022-09-13", "start_date": "2019-07-02"}, {"term": 9, "group": "GREENS", "end_date": null, "start_date": "2022-09-14"}, {"term": 8, "group": "GREENS", "end_date": "2016-12-13", "start_date": "2014-07-01"}, {"term": 8, "group": "GREENS", "end_date": "2019-07-01", "start_date": "2016-12-14"}]</pre> | 1981-11-22 | franziska.keller@europarl.europa.eu | NULL | https://twitter.com/SkaKeller |

After updating fragments, they need to be aggregated explicitly, otherwise the underlying fragments and the data in aggregated table will be out of sync[^views].

[^views]:
    We have previously experimented with materialized views to let the database aggregate fragments declaratively. When using PostgreSQL’s materialized views, the database precomputes a SQL view and stores it to disk, which allows quick read queries even if the view itself is quite complex. Materialized views can even use indexes like a normal table.

    This is great, because it ensures that aggregated records are always in sync with the underlying fragments (as long as the materialized view is refreshed when the fragments change). However, materialized views can only be refreshed as a whole, which can be quite slow for big views. Also, SQLite doesn’t support materialized views (so we’d have to use PostgreSQL instead, which is more complex to deploy and manage).

As we store metadata for every fragment, we can easily compile a full list of sources for every MEP, vote etc. When there’s a need to manually override or change data, we store the override as a fragment, too. This ensures that even if we need to rerun one of the scrapers, the override wouldn’t be affected.
