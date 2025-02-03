import type { JSX } from "preact";

import "./Select.css";

type SelectProps = JSX.SelectHTMLAttributes & {
  options: Record<string, string>;
  value?: string;
};

export default function Select({ options, value = "", ...rest }: SelectProps) {
  return (
    <div class="select">
      <span class="select__label" aria-hidden="true">
        {options[value]}
      </span>

      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 20 20"
        class="select__icon"
        aria-hidden="true"
      >
        <path
          fillRule="evenodd"
          d="M5.22 8.22a.75.75 0 0 1 1.06 0L10 11.94l3.72-3.72a.75.75 0 1 1 1.06 1.06l-4.25 4.25a.75.75 0 0 1-1.06 0L5.22 9.28a.75.75 0 0 1 0-1.06Z"
          clipRule="evenodd"
        />
      </svg>

      <select autoComplete="off" {...rest}>
        {Object.entries(options).map(([optionValue, label]) => (
          <option
            value={optionValue}
            key={optionValue}
            selected={optionValue === value}
          >
            {label}
          </option>
        ))}
      </select>
    </div>
  );
}
