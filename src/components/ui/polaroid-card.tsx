import Link from 'next/link';

interface PolaroidCardProps {
  name: string;
  initials: string;
  status: string;
  statusVariant?: 'critical' | 'stable' | 'default';
  rotation?: number;
  href: string;
  relationship?: string;
  threatType?: string;
}

const statusColors: Record<string, string> = {
  critical: 'bg-neon-magenta/80 text-text-primary',
  stable: 'bg-neon-mint/80 text-surface-0',
  default: 'bg-neon-cyan/60 text-surface-0',
};

export function PolaroidCard({
  name,
  initials,
  status,
  statusVariant = 'default',
  rotation = 0,
  href,
  relationship,
  threatType,
}: PolaroidCardProps) {
  return (
    <Link href={href} className="block shrink-0 w-[160px] touch-active" aria-label={`View profile for ${name}`}>
      <div
        className="relative transition-transform hover:scale-[1.02]"
        style={{ transform: `rotate(${rotation}deg)` }}
      >
        {/* Polaroid frame */}
        <div className="arcane-glass p-1.5 pb-8 shadow-lg">
          {/* Tape strip */}
          <div className="absolute -top-1.5 left-1/2 -translate-x-1/2 w-10 h-2 bg-neon-cyan/15 rounded-sm" />

          {/* Photo placeholder */}
          <div className="aspect-square bg-surface-2 rounded-sm flex items-center justify-center border border-neon-cyan/[0.06]">
            <span className="font-mono text-2xl font-black text-neon-cyan/15">{initials}</span>
          </div>

          {/* ID label */}
          <div className="absolute bottom-10 left-3 font-mono text-[9px] font-bold text-neon-cyan/40">
            ID: #{name.slice(0, 4).toUpperCase()}
          </div>

          {/* Status badge */}
          <div
            className={`absolute bottom-9 right-2 font-mono text-[8px] font-bold px-1.5 py-0.5 rounded-sm ${statusColors[statusVariant]}`}
            style={{ transform: `rotate(${-rotation + 2}deg)` }}
          >
            {status}
          </div>
        </div>

        {/* Name below polaroid */}
        <p className="mt-2 text-center font-mono text-xs font-bold italic text-text-primary truncate">
          {name.toUpperCase().replace(/\s/g, '_')}
        </p>
        {threatType && (
          <p className="text-center font-mono text-[8px] text-neon-cyan/50 truncate italic">
            {threatType}
          </p>
        )}
        {relationship && (
          <p className="text-center font-mono text-[9px] text-text-secondary truncate">
            {relationship}
          </p>
        )}
      </div>
    </Link>
  );
}
