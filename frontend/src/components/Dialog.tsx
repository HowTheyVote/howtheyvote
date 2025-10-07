import type { ComponentChildren } from "preact";
import { createPortal } from "preact/compat";
import { useEffect, useId, useRef } from "preact/hooks";

import "./Dialog.css";
import Icon from "./Icon";

type DialogProps = {
  children: ComponentChildren;
  title: ComponentChildren;
  open?: boolean;
  onOpenChange: (isOpen: boolean) => void;
  className?: string;
};

function Dialog({
  title,
  children,
  open = false,
  onOpenChange,
  className,
}: DialogProps) {
  const ref = useRef<HTMLDialogElement>(null);
  const titleId = useId();

  useEffect(() => {
    if (ref.current && !ref.current.open && open) {
      ref.current.showModal();
    }

    // biome-ignore lint/complexity/useOptionalChain: consistency
    if (ref.current && ref.current.open && !open) {
      ref.current.close();
    }
  }, [open, onOpenChange]);

  // Don’t render dialog server-side, only client-side
  if (typeof window === "undefined") {
    return null;
  }

  const dialog = (
    <dialog
      ref={ref}
      aria-labelledby={titleId}
      class={`dialog ${className || ""}`}
      closedby="any"
      onClose={() => onOpenChange(false)}
    >
      <header class="dialog__header">
        <h2 id={titleId} class="dialog__title gamma">
          {title}
        </h2>
        <button
          type="submit"
          class="dialog__close"
          onClick={() => onOpenChange(false)}
        >
          <Icon name="close" className="dialog__icon" />
          <span class="visually-hidden">Close</span>
        </button>
      </header>
      <div class="dialog__body">{children}</div>
    </dialog>
  );

  return createPortal(dialog, document.body);
}

export default Dialog;
