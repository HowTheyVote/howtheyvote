import type { ComponentChildren } from "preact";
import type { MouseEventHandler } from "preact/compat";
import type { Vote, VotePositionCounts } from "../api";
import { formatDate } from "../lib/dates";
import List from "./List";
import ListItem from "./ListItem";

type EmbedType = "members" | "groups" | "countries";

type DatawrapperLinkProps = {
  type: EmbedType;
  voteId: number;
  title: string;
  timestamp: string;
  stats: VotePositionCounts;
  reference?: string;
  description?: string;
  children?: ComponentChildren;
};

function DatawrapperLink({
  type,
  voteId,
  title,
  timestamp,
  reference,
  description,
  stats,
  children,
}: DatawrapperLinkProps) {
  const onClick: MouseEventHandler<HTMLAnchorElement> = (event) => {
    event.preventDefault();

    const config = getPresetConfig(
      type,
      voteId,
      title,
      timestamp,
      stats,
      reference,
      description,
    );

    const form = document.createElement("form");
    form.target = "_blank";
    form.action = "https://app.datawrapper.de/create/";
    form.method = "POST";

    for (const [key, value] of Object.entries(config)) {
      const input = document.createElement("input");
      input.type = "hidden";
      input.name = key;
      input.value = value;

      form.appendChild(input);
    }

    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
  };

  return (
    // biome-ignore lint/a11y/useValidAnchor: This will soon be a link to a separate page
    <a href="#" onClick={onClick}>
      {children}
    </a>
  );
}

function DataWrapperLinkList({ vote }: { vote: Vote }) {
  return (
    <List space="xxs">
      <ListItem
        title={
          <DatawrapperLink
            type="members"
            voteId={vote.id}
            title={vote.display_title || vote.id.toString()}
            timestamp={vote.timestamp}
            reference={vote.reference}
            description={vote.description}
            stats={vote.stats.total}
          >
            Individual votes
          </DatawrapperLink>
        }
        subtitle={"A searchable table showing how each individual MEP voted."}
      />
      <ListItem
        title={
          <DatawrapperLink
            type="groups"
            voteId={vote.id}
            title={vote.display_title || vote.id.toString()}
            timestamp={vote.timestamp}
            reference={vote.reference}
            description={vote.description}
            stats={vote.stats.total}
          >
            Votes by groups
          </DatawrapperLink>
        }
        subtitle={"A bar chart showing how MEPs of each political group voted."}
      />
      <ListItem
        title={
          <DatawrapperLink
            type="countries"
            voteId={vote.id}
            title={vote.display_title || vote.id.toString()}
            timestamp={vote.timestamp}
            reference={vote.reference}
            description={vote.description}
            stats={vote.stats.total}
          >
            Votes by countries
          </DatawrapperLink>
        }
        subtitle={
          "A bar chart showing how MEPs from different countries voted."
        }
      />
    </List>
  );
}

const GREEN = "rgb(0, 144, 118)";
const RED = "rgb(199, 30, 29)";
const BLUE = "rgb(29, 129, 162)";
const GRAY = "rgb(114, 114, 114)";

function populateConfigForGroups(
  config: Record<string, string>,
  voteId: number,
) {
  config.type = "d3-bars-stacked";
  // Load CSV data from our website
  config.external_data = `https://howtheyvote.eu/api/votes/${voteId}/groups.csv`;

  const metadata: Record<string, object> = {};

  metadata.visualize = {
    "stack-show-absolute": true,
    "color-by-column": true,
    "color-category": {
      map: {
        count_for: GREEN,
        count_against: RED,
        count_abstentions: BLUE,
        count_did_not_vote: GRAY,
      },
      categoryLabels: {
        count_for: "In Favor",
        count_against: "Against",
        count_abstentions: "Abstention",
        count_did_not_vote: "Did not vote",
      },
    },
  };

  metadata.axes = {
    labels: "short_label",
  };

  config.metadata = JSON.stringify(metadata);
}

function populateConfigForCountries(
  config: Record<string, string>,
  voteId: number,
) {
  config.type = "d3-bars-stacked";
  // Load CSV data from our website
  config.external_data = `https://howtheyvote.eu/api/votes/${voteId}/countries.csv`;

  const metadata: Record<string, object> = {};

  metadata.visualize = {
    "stack-show-absolute": true,
    "color-by-column": true,
    "color-category": {
      map: {
        count_for: GREEN,
        count_against: RED,
        count_abstentions: BLUE,
        count_did_not_vote: GRAY,
      },
      categoryLabels: {
        count_for: "In Favor",
        count_against: "Against",
        count_abstentions: "Abstention",
        count_did_not_vote: "Did not vote",
      },
    },
  };

  metadata.axes = {
    labels: "label",
  };

  config.metadata = JSON.stringify(metadata);
}

function populateConfigForMembers(
  config: Record<string, string>,
  voteId: number,
) {
  config.type = "tables";
  // Load CSV data from our website
  config.external_data = `https://howtheyvote.eu/api/votes/${voteId}/members.csv`;

  config.notes = `MEP photos © European Union ${new Date().getFullYear()}`;

  const metadata: Record<string, object> = {};

  // Hide a bunch of columns that aren’t relevant for the visualization
  metadata.data = {
    "column-format": {
      position: {
        ignore: true,
      },
      "member.id": {
        ignore: true,
      },
      "member.last_name": {
        ignore: true,
      },
      "member.first_name": {
        ignore: true,
      },
      "member.group.code": {
        ignore: true,
      },
      "member.group.label": {
        ignore: true,
      },
      "member.country.code": {
        ignore: true,
      },
      "member.country.label": {
        ignore: true,
      },
      "member.group.short_label": {
        ignore: true,
      },
      "member.country.iso_alpha_2": {
        ignore: true,
      },
    },
  };

  // Makes use of Datawrapper’s formula syntax [1] and Markdown support [2]
  // [1]: https://academy.datawrapper.de/article/249-calculations-in-added-columns-and-tooltips
  // [2]: https://academy.datawrapper.de/article/248-how-to-insert-images#tables
  metadata.describe = {
    "computed-columns": [
      {
        name: "Photo",
        formula:
          "CONCAT('<span style=\"display:block;width:41px;height:52px\">![', memberfirst_name, '](', 'https://howtheyvote.eu/api/static/members/', memberid, '-104.jpg)</span>')",
      },
      {
        name: "MEP",
        formula: `CONCAT(
          '<b>', memberfirst_name, ' ', memberlast_name, '</b><br />',
          '<span style="opacity:0.75">', membergroupshort_label, ' · ', membercountrylabel, '</span>'
        )`,
      },
      {
        name: "Vote",
        formula: `CONCAT(
          IF(position == "VotePosition.FOR", "<b style='background:${GREEN}; color:white; padding:1px 4px;'>For</b>", ""),
          IF(position == "VotePosition.AGAINST", "<b style='background:${RED}; color:white; padding:1px 4px;'>Against</b>", ""),
          IF(position == "VotePosition.ABSTENTION", "<b style='background:${BLUE}; color:white; padding:1px 4px'>Abstention</b>", ""),
          IF(position == "VotePosition.DID_NOT_VOTE", "<b style='background:${GRAY}; color:white; padding:1px 4px'>Didn’t vote</b>", "")
        )`,
      },
    ],
  };

  metadata.visualize = {
    columns: {
      Photo: {
        style: {
          fontSize: 3,
        },
        fixedWidth: true,
        width: 0.03,
      },
      Vote: {
        alignment: "right",
      },
    },
    perPage: 10,
    markdown: true,
    noHeader: true,
    pagination: {
      enabled: true,
      position: "both",
    },
    searchable: true,
    mobileFallback: true,
  };

  config.metadata = JSON.stringify(metadata);
}

function getPresetConfig(
  type: EmbedType,
  voteId: number,
  title: string,
  timestamp: string,
  stats: VotePositionCounts,
  reference?: string,
  description?: string,
) {
  // More information about Datawrapper visualization presets:
  // https://developer.datawrapper.de/docs/let-others-create-datawrapper-visualizations-from-presets
  // https://static.dwcdn.net/presets.html
  const config: Record<string, string> = {};

  config.title = title;
  config.description =
    `${formatDate(timestamp)} · ` +
    (reference && `${reference} · `) +
    (description && `${description}</br>`) +
    `<b style="border-bottom: 2px solid ${GREEN};">${stats.FOR} votes in favor</b>, ` +
    `<b style="border-bottom:2px solid ${RED};">${stats.AGAINST} votes against</b>, ` +
    `<b style="border-bottom:2px solid ${BLUE};">${stats.ABSTENTION} abstentions</b>.`;

  config.source_url = `https://howtheyvote.eu/votes/${voteId}`;
  config.source_name = "HowTheyVote.eu (Open Database License)";

  // Skip "Upload" and "Describe" steps in Datawrapper UI
  config.last_edit_step = "2";

  // For some reason, Datawrapper requires that `data` is set even if `external_data` is
  // provided. Has to be a valid JSON string.
  config.data = "{}";

  if (type === "members") populateConfigForMembers(config, voteId);
  if (type === "groups") populateConfigForGroups(config, voteId);
  if (type === "countries") populateConfigForCountries(config, voteId);

  return config;
}

export default DataWrapperLinkList;
