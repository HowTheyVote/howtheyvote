import Button from "./Button";

import "./ShareButton.css";

type ShareButtonProps = {
  title?: string;
  text?: string;
  url: URL | string;
};

export default function ShareButton({ title, text, url }: ShareButtonProps) {
  if (typeof window === "undefined" || !("share" in window.navigator)) {
    return null;
  }

  return (
    <Button
      className="share-button"
      style="block"
      size="lg"
      onClick={() =>
        window.navigator.share({ title, text, url: url.toString() })
      }
    >
      Share this vote!
    </Button>
  );
}
