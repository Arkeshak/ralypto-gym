import { useEffect, useState } from "react";
import { ArrowRight, Check, Search, X } from "lucide-react";
import { createPortal } from "react-dom";
import type { MemberStatus } from "../data/demo";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "normal" | "small";
};

export function Button({
  children,
  variant = "secondary",
  size = "normal",
  className = "",
  type = "button",
  ...props
}: ButtonProps) {
  return (
    <button
      className={`button button-${variant} button-${size} ${className}`}
      type={type}
      {...props}
    >
      {children}
    </button>
  );
}

export function SectionHeading({
  title,
  description,
  action,
}: {
  title: string;
  description?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="section-heading">
      <div>
        <h2>{title}</h2>
        {description && <p className="muted-copy">{description}</p>}
      </div>
      {action}
    </div>
  );
}

export function StatusPill({ status }: { status: MemberStatus | string }) {
  const label = status.replace("_", " ");
  return <span className={`status-pill status-${status}`}>{label}</span>;
}

export function Avatar({
  name,
  color,
  size = "normal",
}: {
  name: string;
  color?: string;
  size?: "small" | "normal" | "large";
}) {
  const initials = name
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part.charAt(0))
    .join("")
    .toUpperCase();
  return (
    <span className={`avatar avatar-${size}`} style={{ "--avatar-tint": color ?? "#b5f24a" } as React.CSSProperties}>
      {initials}
    </span>
  );
}

export function Modal({
  title,
  description,
  open,
  onClose,
  children,
  footer,
}: {
  title: string;
  description?: string;
  open: boolean;
  onClose: () => void;
  children: React.ReactNode;
  footer?: React.ReactNode;
}) {
  useEffect(() => {
    if (!open) return;
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose, open]);

  if (!open) return null;
  return createPortal(
    <div className="modal-backdrop" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <section className="modal-panel" role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <header className="modal-heading">
          <div>
            <h2 id="modal-title">{title}</h2>
            {description && <p>{description}</p>}
          </div>
          <button className="icon-button modal-close" onClick={onClose} aria-label="Close dialog">
            <X size={18} />
          </button>
        </header>
        <div className="modal-content">{children}</div>
        {footer && <footer className="modal-footer">{footer}</footer>}
      </section>
    </div>,
    document.body,
  );
}

export function SearchInput({
  value,
  onChange,
  placeholder = "Search",
  ariaLabel = "Search",
}: {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  ariaLabel?: string;
}) {
  return (
    <label className="search-input">
      <Search size={16} aria-hidden="true" />
      <input
        type="search"
        aria-label={ariaLabel}
        placeholder={placeholder}
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
      {value && (
        <button type="button" className="icon-button search-clear" aria-label="Clear search" onClick={() => onChange("")}>
          <X size={14} />
        </button>
      )}
    </label>
  );
}

export function PageIntro({
  title,
  description,
  action,
}: {
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  return (
    <header className="page-intro">
      <div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {action}
    </header>
  );
}

export function EmptyState({
  title,
  description,
  action,
}: {
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="empty-state">
      <div className="empty-state-mark">
        <Check size={20} />
      </div>
      <h3>{title}</h3>
      <p>{description}</p>
      {action}
    </div>
  );
}

export function Toggle({
  checked,
  onChange,
  label,
}: {
  checked: boolean;
  onChange: (value: boolean) => void;
  label: string;
}) {
  return (
    <button
      className={`toggle ${checked ? "toggle-on" : ""}`}
      type="button"
      role="switch"
      aria-checked={checked}
      aria-label={label}
      onClick={() => onChange(!checked)}
    >
      <span />
    </button>
  );
}

export function ConfirmAction({
  label = "Confirm",
  onConfirm,
  onCancel,
}: {
  label?: string;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  return (
    <div className="confirm-action">
      <Button variant="primary" onClick={onConfirm}>
        <Check size={16} />
        {label}
      </Button>
      <Button variant="ghost" onClick={onCancel}>
        Cancel
        <ArrowRight size={15} />
      </Button>
    </div>
  );
}

export function useModalState() {
  const [open, setOpen] = useState(false);
  return { open, show: () => setOpen(true), close: () => setOpen(false) };
}
