import Select from "./Select";

type SortSelectProps = {
  value?: string;
};

export default function SortSelect({ value }: SortSelectProps) {
  return (
    <Select
      value={value}
      options={{
        relevance: "Relevance",
        newest: "Newest first",
        oldest: "Oldest first",
      }}
      onChange={(event) => {
        const searchParams = new URLSearchParams(window.location.search);
        const value = event.currentTarget.value;
        searchParams.set("sort", value);
        window.location.search = searchParams.toString();
      }}
    />
  );
}
