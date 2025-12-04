import { bem } from "../lib/bem";
import Button from "./Button";
import Input from "./Input";

import "./SearchForm.css";

type SearchFormProps = {
  action?: string;
  size?: "lg";
  style?: "elevated" | "dark";
  value?: string;
};

export default function SearchForm({
  action,
  size,
  style,
  value,
}: SearchFormProps) {
  return (
    <form class={bem("search-form", style)} method="get" action={action}>
      <Input
        type="search"
        size={size}
        name="q"
        className="search-form__input"
        placeholder="Search for keywords…"
        value={value}
      />
      <Button
        style="fill"
        size={size}
        className="search-form__submit"
        type="submit"
      >
        Search
      </Button>
    </form>
  );
}
