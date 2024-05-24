import "./StatsCard.css";

type StatsCardProps = {
  value?: string | null;
  label?: string | null;
};

export default function StatsCard({ value, label }: StatsCardProps) {
  return (
    <div class="stats-card">
      <span class="stats-card__value">{value}</span>{" "}
      <span class="stats-card__label">{label}</span>
    </div>
  );
}
