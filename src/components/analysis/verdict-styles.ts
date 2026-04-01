export const VERDICT_STYLES: Record<string, { bg: string; border: string; text: string; glow: string; label: string }> = {
  RED_FLAG: {
    bg: 'bg-neon-magenta/10',
    border: 'border-neon-magenta/30',
    text: 'text-neon-magenta',
    glow: 'text-glow-magenta',
    label: 'RED FLAG',
  },
  YELLOW_FLAG: {
    bg: 'bg-warning-amber/10',
    border: 'border-warning-amber/30',
    text: 'text-warning-amber',
    glow: '',
    label: 'YELLOW FLAG',
  },
  GREEN_FLAG: {
    bg: 'bg-neon-mint/10',
    border: 'border-neon-mint/30',
    text: 'text-neon-mint',
    glow: '',
    label: 'GREEN FLAG',
  },
};
