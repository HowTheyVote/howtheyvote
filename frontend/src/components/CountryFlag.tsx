type CountryFlagProps = {
  code: string;
};

const FLAGS: Record<string, string> = {
  AUT: "🇦🇹",
  BEL: "🇧🇪",
  BGR: "🇧🇬",
  CYP: "🇨🇾",
  CZE: "🇨🇿",
  DEU: "🇩🇪",
  DNK: "🇩🇰",
  EST: "🇪🇪",
  ESP: "🇪🇸",
  FIN: "🇫🇮",
  FRA: "🇫🇷",
  GBR: "🇬🇧",
  GRC: "🇬🇷",
  HRV: "🇭🇷",
  HUN: "🇭🇺",
  IRE: "🇮🇪",
  ITA: "🇮🇹",
  LTU: "🇱🇹",
  LUX: "🇱🇺",
  LVA: "🇱🇻",
  MLT: "🇲🇹",
  NLD: "🇳🇱",
  POL: "🇵🇱",
  PRT: "🇵🇹",
  ROU: "🇷🇴",
  SWE: "🇸🇪",
  SVN: "🇸🇮",
  SVK: "🇸🇰",
};

function CountryFlag({ code }: CountryFlagProps) {
  if (!FLAGS[code]) {
    return null;
  }

  return <>{FLAGS[code]}</>;
}

export default CountryFlag;
