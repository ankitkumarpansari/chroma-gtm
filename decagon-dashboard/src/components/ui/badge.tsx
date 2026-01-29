import { cn } from "../../lib/utils";

type BadgeVariant =
  | "default"
  | "highest"
  | "high"
  | "medium-high"
  | "strategic"
  | "emerging"
  | "new"
  | "researching"
  | "contacted"
  | "success"
  | "warning";

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  className?: string;
}

const variantStyles: Record<BadgeVariant, string> = {
  default: "bg-neutral-200 text-neutral-700 dark:bg-neutral-800 dark:text-neutral-300",
  highest: "bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-300",
  high: "bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-300",
  "medium-high": "bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-300",
  strategic: "bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-300",
  emerging: "bg-neutral-200 text-neutral-600 dark:bg-neutral-500/20 dark:text-neutral-300",
  new: "bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-300",
  researching: "bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-300",
  contacted: "bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-300",
  success: "bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-300",
  warning: "bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-300",
};

export function Badge({ children, variant = "default", className }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
        variantStyles[variant],
        className
      )}
    >
      {children}
    </span>
  );
}

export function getBadgeVariant(value: string): BadgeVariant {
  const normalized = value.toLowerCase().replace(/\s+/g, "-");
  if (normalized in variantStyles) {
    return normalized as BadgeVariant;
  }
  return "default";
}
