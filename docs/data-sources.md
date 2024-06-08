# Data Sources

HowTheyVote consumes data from multiple official sources. This page lists the individual sources and how we use them in HowTheyVote.

## Members of the European Parliament

| Source | Scraper | Example | Usage |
| --- | --- | --- | --- |
| MEP Directory Index | `members.MembersScraper` | [Link](https://www.europarl.europa.eu/meps/en/directory/xml?leg=9) | Retrieving a list of all MEP IDs for a given legislature |
| MEP Profile | `members.MemberInfoScraper` | [Link](https://www.europarl.europa.eu/meps/en/96734/SKA_KELLER/home) | Biographical information (name, date of birth, nationality) and contact information |
| History of parliamentary service | `members.MemberGroupsScraper` | [Link](https://www.europarl.europa.eu/meps/en/96734/SKA_KELLER/history/9#detailedcardmep) | MEP group memberships with start and end dates |

All data sources listed above use a single ID to identify individual MEPs. The ID is consistent across legislatures. HowTheyVote uses these IDs (instead of assigning its own IDs) and merges data from multiple sources based on these IDs.

## Plenary sessions

| Source | Scraper | Example | Usage |
| --- | --- | --- | --- |
| Plenary Calendar JSON Endpoint | `sessions.SessionsScraper` | [Link](https://www.europarl.europa.eu/plenary/en/ajax/getSessionCalendar.html?family=PV&termId=9) | Retrieving a list of all plenary sessions for a given legislature |

## Votes

| Source | Scraper | Example | Usage |
| --- | --- | --- | --- |
| Roll-call vote (RCV) list | `votes.RCVListScraper` | [Link](https://www.europarl.europa.eu/doceo/document/PV-9-2023-05-10-RCV_FR.xml) | Retrieving vote metadata (titles, dates, …) and voting behavior of individual MEPs for all roll-call votes on a given date |
| Legislative Observatory procedure file | `votes.OeilTitleScraper` | [Link](https://oeil.secure.europarl.europa.eu/oeil/popups/ficheprocedure.do?reference=2022/2081(DEC)&l=en) | Retrieving a title for a given vote in case a title could not be extracted from the RCV list data |

We use the the `Identifier` attribute in RCV lists as vote IDs in HowTheyVote. We extract references to documents such as reports and resolutions (e.g. `A9-0101/2023`) to find the corresponding procedure file in the Legislative Observatory.

Most RCV lists contain a `PersId` that identifies individual MEPs using the IDs also used in the MEP Directory. If present, we use this attribute to associate voting data from RCV lists with the MEP records in our database. Older RCV lists are missing the `PersId` attribute. In these cases, we’re associating voting data with MEP records using MEP names (considering only MEPs that have been active on the day of the vote).
