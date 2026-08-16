import fs from "node:fs";
import type { Request } from "@tinyhttp/app";
import type { AsnResponse, CountryResponse } from "mmdb-lib";
import * as mmdb from "mmdb-lib";
import {
  GEOLITE2_ASN_PATH,
  GEOLITE2_COUNTRY_PATH,
  PUBLIC_URL,
} from "../config";

const asnReader = new mmdb.Reader<AsnResponse>(
  fs.readFileSync(GEOLITE2_ASN_PATH),
);
const countryReader = new mmdb.Reader<CountryResponse>(
  fs.readFileSync(GEOLITE2_COUNTRY_PATH),
);

type EnrichedRequestData = {
  referrerHeader?: string;
  referrerUrlParam?: string;
  country?: string;
  countryName?: string;
  asn?: number;
  asName?: string;
};

export function enrichRequest(request: Request) {
  const data: EnrichedRequestData = {};
  const url = new URL(request.url, PUBLIC_URL);
  const referrer = request.headers.referer;
  const ipAddress = request.headersDistinct["x-forwarded-for"]?.[0];

  if (referrer) {
    try {
      data.referrerHeader = new URL(referrer).hostname;
    } catch {}
  }

  data.referrerUrlParam = url.searchParams.get("utm_source") || undefined;

  if (ipAddress) {
    const country = countryReader.get(ipAddress)?.country;
    data.country = country?.iso_code;
    data.countryName = country?.names.en;

    const asn = asnReader.get(ipAddress);
    data.asn = asn?.autonomous_system_number;
    data.asName = asn?.autonomous_system_organization;
  }

  return data;
}
