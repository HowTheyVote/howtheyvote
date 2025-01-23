import type { JSX } from "preact/jsx-runtime";
import type { Group } from "../api";
import Select from "./Select";

type GroupsFilterSelectProps = {
  groups: Array<Group>;
  value?: string;
  onChange?: JSX.GenericEventHandler<HTMLSelectElement>;
};

export default function GroupsFilterSelect({
  groups,
  value,
  onChange,
}: GroupsFilterSelectProps) {
  const options = Object.fromEntries(
    groups
      .map((group) => [group.code, group.short_label || group.label])
      .sort((a, b) => a[1].localeCompare(b[1])),
  );

  return (
    <Select
      options={{
        "": "All groups",
        ...options,
      }}
      value={value}
      onChange={onChange}
    />
  );
}
