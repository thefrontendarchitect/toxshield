interface StatusBadgeProps {
  label: string;
  variant?: 'critical' | 'warning' | 'stable' | 'default';
  className?: string;
}

const variantStyles: Record<string, string> = {
  critical: 'badge-status',
  warning: 'bg-warning-amber/10 text-warning-amber border border-warning-amber/20 font-mono text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded',
  stable: 'bg-neon-mint/10 text-neon-mint border border-neon-mint/20 font-mono text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded',
  default: 'bg-neon-cyan/10 text-neon-cyan/60 border border-neon-cyan/10 font-mono text-[10px] font-medium uppercase tracking-wider px-2.5 py-1 rounded',
};

export function StatusBadge({ label, variant = 'default', className = '' }: StatusBadgeProps) {
  return (
    <span className={`${variantStyles[variant]} ${className}`}>
      {label}
    </span>
  );
}
