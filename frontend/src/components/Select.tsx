import type { JSX } from "preact";
import Icon from "./Icon";

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

      <Icon name="chevron-down" />

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
