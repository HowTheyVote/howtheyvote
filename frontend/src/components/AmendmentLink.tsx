import Icon from "./Icon";

type AmendmentLinkProps = {
  amendmentNumber: number | string;
  className?: string;
  showIcon?: boolean;
  url: string;
};

export default function AmendmentLink({
  amendmentNumber,
  className,
  showIcon = false,
  url,
}: AmendmentLinkProps) {
  return (
    <a
      class={className}
      href={url}
      target="_blank"
      rel="noreferrer noopener"
      onClick={() =>
        window.alert(
          `The linked document may contain other amendments in addition to amendment ${amendmentNumber}. Please make sure you read the correct amendment.`,
        )
      }
    >
      {showIcon && <Icon name="external-link" />}
      Am {amendmentNumber}
    </a>
  );
}
