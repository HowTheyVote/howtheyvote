import type { JSX } from "preact/jsx-runtime";

import "./FilterSelect.css";

type FilterSelectProps = {
  options: Record<string, string>;
  onChange?: JSX.GenericEventHandler<HTMLSelectElement>;
  value?: string;
};

export default function FilterSelect({
  options,
  onChange,
  value = "",
}: FilterSelectProps) {
  return (
    <div class="filter-select">
      <span class="filter-select__label" aria-hidden="true">
        {options[value]}
      </span>

      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 20 20"
        class="filter-select__icon"
        aria-hidden="true"
      >
        <path
          fillRule="evenodd"
          d="M5.22 8.22a.75.75 0 0 1 1.06 0L10 11.94l3.72-3.72a.75.75 0 1 1 1.06 1.06l-4.25 4.25a.75.75 0 0 1-1.06 0L5.22 9.28a.75.75 0 0 1 0-1.06Z"
          clipRule="evenodd"
        />
      </svg>

      <select
        onChange={(event) => {
          if (onChange) {
            onChange(event);
          }
        }}
        autoComplete="off"
      >
        {Object.entries(options).map(([value, label]) => (
          <option value={value} key={value}>
            {label}
          </option>
        ))}
      </select>
    </div>
  );
}
