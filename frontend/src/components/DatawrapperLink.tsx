import type { ComponentChildren } from "preact";
import type { MouseEventHandler } from "preact/compat";
import type { VotePositionCounts } from "../api";
import { formatDate } from "../lib/dates";

type DatawrapperLinkProps = {
  voteId: number;
  title: string;
  timestamp: string;
  stats: VotePositionCounts;
  reference?: string;
  description?: string;
  children?: ComponentChildren;
};

function DatawrapperLink({
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

const GREEN = "rgb(0, 144, 118)";
const RED = "rgb(199, 30, 29)";
const BLUE = "rgb(29, 129, 162)";
const GRAY = "rgb(114, 114, 114)";

function getPresetConfig(
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

  config.type = "tables";

  config.title = title;
  config.description =
    `${formatDate(timestamp)} · ` +
    (reference && `${reference} · `) +
    (description && `${description} · `) +
    `<b style="border-bottom: 2px solid ${GREEN};">${stats.FOR} votes in favor</b>, ` +
    `<b style="border-bottom:2px solid ${RED};">${stats.AGAINST} votes against</b>, ` +
    `<b style="border-bottom:2px solid ${BLUE};">${stats.ABSTENTION} abstentions</b>.`;
  config.notes = `MEP photos © European Union ${new Date().getFullYear()}`;
  config.source_name = "HowTheyVote.eu (Open Database License)";
  config.source_url = `https://howtheyvote.eu/votes/${voteId}`;

  // Skip "Upload" and "Describe" steps in Datawrapper UI
  config.last_edit_step = "2";

  // Load CSV data from our website
  config.external_data = `https://howtheyvote.eu/api/votes/${voteId}/members.csv`;

  // For some reason, Datawrapper requires that `data` is set even if `external_data` is
  // provided. Has to be a valid JSON string.
  config.data = "{}";

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

  return config;
}

export default DatawrapperLink;
