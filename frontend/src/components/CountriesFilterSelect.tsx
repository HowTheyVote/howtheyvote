import type { JSX } from "preact/jsx-runtime";
import type { Country } from "../api";
import FilterSelect from "./FilterSelect";

type CountriesFilterSelectProps = {
  countries: Array<Country>;
  value?: string;
  onChange?: JSX.GenericEventHandler<HTMLSelectElement>;
};

export default function CountriesFilterSelect({
  countries,
  value,
  onChange,
}: CountriesFilterSelectProps) {
  const options = Object.fromEntries(
    countries
      .map((country) => [country.code, country.label])
      .sort((a, b) => a[1].localeCompare(b[1])),
  );

  return (
    <FilterSelect
      options={{
        "": "All countries",
        ...options,
      }}
      value={value}
      onChange={onChange}
    />
  );
}
