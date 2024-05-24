import { bem } from "../lib/bem";
import Button from "./Button";
import Input from "./Input";

import "./SearchForm.css";

type SearchFormProps = {
  style?: "elevated" | "dark";
  value?: string;
};

export default function SearchForm({ style, value }: SearchFormProps) {
  return (
    <form class={bem("search-form", style)} method="get" action="/votes">
      <Input
        type="search"
        size="lg"
        name="q"
        className="search-form__input"
        placeholder="Search for keywords…"
        value={value}
      />
      <Button
        style="fill"
        size="lg"
        className="search-form__submit"
        type="submit"
      >
        Search
      </Button>
    </form>
  );
}
