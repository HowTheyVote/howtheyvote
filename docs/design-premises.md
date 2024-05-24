# Design Premises

## Narrow scope

HowTheyVote is a project run by volunteers, and it’s already quite ambitious. While it might be cool to integrate additional related data (e.g. amendments, full legislative process), our primary focus is voting data.

## A tool for everyone

Our goal is to make voting data accessible to citizens. We are happy if HowTheyVote is a useful tool for professional working in non-profits, politics, or journalism, but these users are not our focus. When adding new features, we should always consider whether they will provide value for non-professional useres. We should be careful to add features that only provide value for professional users.

## Automate as much as possible

The time we can spend working on HowTheyVote is limited. This means we should focus on providing data that can be retrieved and integrated in fully automated ways. We shouldn’t add data pipelines that need constant babysitting.

## Make data available as soon as possible

Media attention for votes drops quickly after votes have been cast in plenary. We should always try to make voting data available as soon as possible. If there are additional data sources that could enrich voting data, but are avaiable only with a delay of multiple days, integrating these data sources should be optional.

## Missing data is better than incorrect data

We should add safeguards to our data pipelines. When there is doubt about the correctness of the data our pipelines produce, we should prefer not displaying the data. For example, if the total number of MEPs for a vote doesn’t match the expected number (704 MEPs post-Brexit), we should flag the vote for review.

## English only

While the European Parliament does translate most documents and data sources into all of its working languages or even into all languages spoken in its member states, these translations are often published with a significant delay. Storing translated data and translating UIs is a significant effort. We should avoid the resulting complexity, at least for now.

## API first

Being able to view and search vote results is nice, sure. But we want other people to be able to build analyses, visualization, and more on top of the data HowTheyVote provides. All data that can be viewed on our website should also be available via the API.

## Few dependencies

Before you add new dependencies, think whether that’s actually necessary. No one wants to review dozenzs of Dependabot PRs every month.

## Simple and cheap infrastructure

While HowTheyVote has received some initial funding, the project currently doesn’t have any revenue sources (and we do not plan to change this at the moment). We shouldn’t be wasteful with resources, so we can run this project sustainability, even without securing any future funding.

We should also make sure that we can migrate off to another provider without making major changes to the application or spending signficant amounts of time on the migration. HowTheyVote shouldn’t go offline just because a random provider has run out of VC money.
