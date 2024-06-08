import type { JSX } from "preact/jsx-runtime";
import FilterSelect from "./FilterSelect";

type PositionFilterSelectProps = {
  value?: string;
  onChange?: JSX.GenericEventHandler<HTMLSelectElement>;
};

export default function PositionFilterSelect({
  value,
  onChange,
}: PositionFilterSelectProps) {
  const options = {
    "": "All positions",
    FOR: "For",
    AGAINST: "Against",
    ABSTENTION: "Abstention",
    DID_NOT_VOTE: "Did not vote",
  };

  return <FilterSelect value={value} options={options} onChange={onChange} />;
}
