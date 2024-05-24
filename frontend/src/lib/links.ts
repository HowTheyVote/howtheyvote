import { BACKEND_PUBLIC_URL, PUBLIC_URL } from "../config";

type ErrorType = "MISSING" | "INCORRECT_RESULT" | "OTHER";
type ErrorData = { voteId?: number };
const ERROR_REPORT_FORM_URL = "https://tally.so/r/w2eb1M";
const ERROR_TYPE_MAPPING: Record<ErrorType, string> = {
  MISSING: "Missing vote",
  INCORRECT_RESULT: "Incorrect vote results",
  OTHER: "Other",
};

export function getErrorReportFormUrl(type?: ErrorType, data?: ErrorData) {
  const url = new URL(ERROR_REPORT_FORM_URL);

  if (type) {
    url.searchParams.set("type", ERROR_TYPE_MAPPING[type]);
  }

  if (data?.voteId) {
    const link = new URL(`/votes/${data.voteId}`, PUBLIC_URL);
    url.searchParams.set("link", link.toString());
  }

  return url.toString();
}

type DataFormat = "json" | "csv";

export function getDownloadUrl(voteId: number, format: DataFormat): string {
  const url = new URL(`/api/votes/${voteId}`, BACKEND_PUBLIC_URL);

  if (format === "csv") {
    return `${url.toString()}.csv`;
  }

  return url.toString();
}
