import {
  BrainIcon,
  ShieldIcon,
  PulseIcon,
  EyeIcon,
  WarningIcon,
  HeartCrackIcon,
  FingerprintIcon,
  DocumentIcon,
} from '@/components/ui/dossier-icons';
import type { ComponentType } from 'react';
import { ICON_KEYS, type IconKey } from './icon-keys';

const ICON_MAP: Record<IconKey, ComponentType<{ size?: number; className?: string }>> = {
  brain: BrainIcon,
  shield: ShieldIcon,
  pulse: PulseIcon,
  eye: EyeIcon,
  warning: WarningIcon,
  heart: HeartCrackIcon,
  fingerprint: FingerprintIcon,
  document: DocumentIcon,
};

// Map pattern area names to icon keys for old data that has emojis instead of keys
const AREA_TO_ICON: Record<string, IconKey> = {
  'communication style': 'brain',
  'communication': 'brain',
  'emotional regulation': 'pulse',
  'emotional patterns': 'pulse',
  'emotional stability': 'pulse',
  'boundary setting': 'shield',
  'boundary awareness': 'shield',
  'boundaries': 'shield',
  'conflict resolution': 'warning',
  'conflict': 'warning',
  'people pleasing': 'heart',
  'relationship patterns': 'heart',
  'relationship': 'heart',
  'self-awareness': 'eye',
  'awareness': 'eye',
  'professional assertiveness': 'fingerprint',
  'assertiveness': 'fingerprint',
  'identity': 'fingerprint',
};

function isIconKey(value: string): value is IconKey {
  return (ICON_KEYS as readonly string[]).includes(value);
}

function resolveIconKey(area?: string): IconKey {
  if (area) {
    const key = AREA_TO_ICON[area.toLowerCase()];
    if (key) return key;
  }
  return 'eye';
}

export function PatternIcon({ icon, area, size = 16, className = 'text-text-secondary' }: { icon: string; area?: string; size?: number; className?: string }) {
  const key = isIconKey(icon) ? icon : resolveIconKey(area);
  const Icon = ICON_MAP[key];
  return <Icon size={size} className={className} />;
}
