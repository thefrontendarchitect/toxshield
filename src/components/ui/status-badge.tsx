interface StatusBadgeProps {
  label: string;
  variant?: 'critical' | 'warning' | 'stable' | 'default';
  className?: string;
}

const variantStyles: Record<string, string> = {
  critical: 'badge-status',
  warning: 'bg-white/10 text-white/70 font-mono text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-sm',
  stable: 'bg-white/5 text-white/40 font-mono text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-sm',
  default: 'bg-white/5 text-white/30 font-mono text-[10px] font-medium uppercase tracking-wider px-2.5 py-1 rounded-sm',
};

export function StatusBadge({ label, variant = 'default', className = '' }: StatusBadgeProps) {
  return (
    <span className={`${variantStyles[variant]} ${className}`}>
      {label}
    </span>
  );
}
