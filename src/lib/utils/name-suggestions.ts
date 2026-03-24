const QUIRKY_SUFFIXES = [
  'the Phantom',
  'the Ghost',
  'the Shadow',
  'the Glitch',
  'the Clone',
  '2.0',
  'v2',
  'Redux',
  'Reloaded',
  'the Sequel',
  'Strikes Back',
  'Returns',
  'Unchained',
  'Unplugged',
  'After Dark',
];

export type InputType = 'text_description' | 'whatsapp_chat' | 'slack_chat';

const SOURCE_LABELS: Record<InputType, string> = {
  whatsapp_chat: 'from WhatsApp',
  slack_chat: 'from Slack',
  text_description: 'the Other',
};

/**
 * Generate quirky disambiguated names when a person with the same name already exists.
 * Returns 5 suggestions — a mix of fun suffixes, source-based, and relationship-based.
 */
export function generateQuirkyNames(
  baseName: string,
  inputType: InputType,
  relationship?: string | null,
): string[] {
  const names = new Set<string>();

  // Source-based name (always include)
  const sourceLabel = SOURCE_LABELS[inputType] || 'the Other';
  names.add(`${baseName} ${sourceLabel}`);

  // Relationship-based name (if provided)
  if (relationship) {
    names.add(`${baseName} the ${capitalize(relationship)}`);
  }

  // Shuffle and pick from quirky pool
  const shuffled = [...QUIRKY_SUFFIXES].sort(() => Math.random() - 0.5);

  for (const suffix of shuffled) {
    if (names.size >= 5) break;
    names.add(`${baseName} ${suffix}`);
  }

  return Array.from(names).slice(0, 5);
}

function capitalize(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}
