import { bem } from "../lib/bem";
import "./Avatar.css";

type AvatarProps = {
  url: string;
  style?: "square";
};

export default function Avatar({ url, style }: AvatarProps) {
  return (
    <div className={bem("avatar", style)}>
      <img src={url} alt="" loading="lazy" />
    </div>
  );
}
