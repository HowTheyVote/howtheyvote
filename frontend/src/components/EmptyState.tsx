import type { ComponentChildren } from "preact";

import "./EmptyState.css";

type EmptyStateProps = {
  children?: ComponentChildren;
  action?: ComponentChildren;
};

export default function EmptyState({ children, action }: EmptyStateProps) {
  return (
    <div class="empty-state">
      <p>{children}</p>
      {action}
    </div>
  );
}
