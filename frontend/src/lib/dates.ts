import * as config from "../config";

function ensureDate(date: Date | string): Date {
  if (typeof date === "string") {
    return new Date(date);
  }

  return date;
}

export function formatDateTime(date?: Date | string): string | null {
  if (!date) {
    return null;
  }

  const dateObj = ensureDate(date);

  return dateObj.toLocaleTimeString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "numeric",
    hour12: false,
    timeZone: config.TIMEZONE,
  });
}

type DateFormat = "short" | "default" | "long";

export function formatDate(
  date?: Date | string,
  format: DateFormat = "default",
): string | null {
  if (!date) {
    return null;
  }

  const dateObj = ensureDate(date);

  const formats: Record<DateFormat, object> = {
    default: { year: "numeric", month: "short", day: "numeric" },
    short: { month: "short", day: "numeric" },
    long: { year: "numeric", month: "long", day: "numeric" },
  };

  return dateObj.toLocaleDateString("en-US", formats[format]);
}

export function formatNumber(number?: number): string | null {
  if (!number) {
    return null;
  }

  return number.toLocaleString("en-US");
}

export function isValidDate(date: Date) {
  // https://stackoverflow.com/a/38182068
  return !Number.isNaN(date.getTime());
}

export function toISODateString(date: Date) {
  const year = date.getFullYear();
  const month = (date.getMonth() + 1).toString().padStart(2, "0");
  const day = date.getDate().toString().padStart(2, "0");

  return `${year}-${month}-${day}`;
}
