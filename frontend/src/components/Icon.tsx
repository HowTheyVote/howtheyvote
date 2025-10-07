import "./Icon.css";

type IconProps = {
  name: string;
  className?: string;
};

function Icon({ name, className }: IconProps) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 20 20"
      class={`icon ${className || ""}`}
      aria-hidden="true"
    >
      <use href={`/static/icons.svg#${name}`} />
    </svg>
  );
}

export default Icon;
