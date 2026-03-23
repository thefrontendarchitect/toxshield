import { parseString } from 'whatsapp-chat-parser';

interface ParsedMessage {
  date: Date;
  message: string;
}

export interface ParsedChat {
  participants: string[];
  messagesByParticipant: Record<string, ParsedMessage[]>;
  totalMessages: number;
  dateRange: { from: Date; to: Date } | null;
}

export interface ParticipantSummary {
  name: string;
  messageCount: number;
  firstMessage: Date;
  lastMessage: Date;
}

/**
 * Parse a WhatsApp chat export (.txt) and extract participants + messages.
 * Filters out system messages (author === null).
 */
export function parseWhatsAppExport(text: string): ParsedChat {
  const messages = parseString(text, { parseAttachments: false });

  const messagesByParticipant: Record<string, ParsedMessage[]> = {};
  let totalMessages = 0;
  let earliest: Date | null = null;
  let latest: Date | null = null;

  for (const msg of messages) {
    // Skip system messages
    if (!msg.author) continue;

    totalMessages++;

    if (!messagesByParticipant[msg.author]) {
      messagesByParticipant[msg.author] = [];
    }

    messagesByParticipant[msg.author].push({
      date: msg.date,
      message: msg.message,
    });

    if (!earliest || msg.date < earliest) earliest = msg.date;
    if (!latest || msg.date > latest) latest = msg.date;
  }

  const participants = Object.keys(messagesByParticipant).sort(
    (a, b) => (messagesByParticipant[b]?.length ?? 0) - (messagesByParticipant[a]?.length ?? 0)
  );

  return {
    participants,
    messagesByParticipant,
    totalMessages,
    dateRange: earliest && latest ? { from: earliest, to: latest } : null,
  };
}

/**
 * Get summary info for each participant (for the picker UI).
 */
export function getParticipantSummaries(parsed: ParsedChat): ParticipantSummary[] {
  return parsed.participants.map((name) => {
    const msgs = parsed.messagesByParticipant[name] ?? [];
    const dates = msgs.map((m) => m.date).sort((a, b) => a.getTime() - b.getTime());

    return {
      name,
      messageCount: msgs.length,
      firstMessage: dates[0] ?? new Date(),
      lastMessage: dates[dates.length - 1] ?? new Date(),
    };
  });
}

/**
 * Format chat messages for AI analysis.
 * Includes ALL participants' messages (context matters for conversation patterns)
 * but marks the target person clearly.
 *
 * Prioritizes recent messages, keeps samples from earlier for pattern detection.
 * Stays within ~8000 chars to fit comfortably in the AI token budget.
 */
export function formatChatForAnalysis(
  targetPerson: string,
  allParticipantMessages: Record<string, ParsedMessage[]>,
  maxChars = 8000
): string {
  // Merge all messages into a single chronological list
  const allMessages: Array<{ author: string; date: Date; message: string }> = [];

  for (const [author, msgs] of Object.entries(allParticipantMessages)) {
    for (const msg of msgs) {
      allMessages.push({ author, date: msg.date, message: msg.message });
    }
  }

  // Sort chronologically
  allMessages.sort((a, b) => a.date.getTime() - b.date.getTime());

  // Format each message
  const formatMsg = (m: { author: string; date: Date; message: string }) => {
    const dateStr = m.date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
    const timeStr = m.date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    });
    const marker = m.author === targetPerson ? ' [TARGET]' : '';
    return `[${dateStr} ${timeStr}] ${m.author}${marker}: ${m.message}`;
  };

  // Strategy: take last N messages that fit, plus a sample from the beginning
  const formatted = allMessages.map(formatMsg);

  // Start from the end (most recent) and work backward
  const result: string[] = [];
  let currentChars = 0;
  const earlyBudget = Math.floor(maxChars * 0.2); // 20% for early messages
  const recentBudget = maxChars - earlyBudget;

  // Recent messages (last 80% of budget)
  for (let i = formatted.length - 1; i >= 0; i--) {
    const line = formatted[i];
    if (currentChars + line.length + 1 > recentBudget) break;
    result.unshift(line);
    currentChars += line.length + 1;
  }

  // Early messages (first 20% of budget) — only if we didn't already include them
  const earliestIncluded = result.length > 0 ? 0 : -1;
  if (earliestIncluded >= 0 && formatted.length > result.length + 10) {
    const earlyMessages: string[] = [];
    let earlyChars = 0;

    for (let i = 0; i < formatted.length; i++) {
      if (result[0] === formatted[i]) break; // reached the recent portion
      const line = formatted[i];
      if (earlyChars + line.length + 1 > earlyBudget) break;
      earlyMessages.push(line);
      earlyChars += line.length + 1;
    }

    if (earlyMessages.length > 0) {
      result.unshift('--- earlier messages ---', ...earlyMessages, '--- ... ---');
    }
  }

  const targetMsgCount = allMessages.filter((m) => m.author === targetPerson).length;
  const totalIncluded = result.filter((r) => r.startsWith('[')).length;

  const header = `WhatsApp conversation analysis — Target: ${targetPerson}
Total messages from ${targetPerson}: ${targetMsgCount}
Messages shown: ${totalIncluded} of ${allMessages.length}
${allMessages.length > 0 ? `Date range: ${allMessages[0].date.toLocaleDateString()} → ${allMessages[allMessages.length - 1].date.toLocaleDateString()}` : ''}
---
`;

  return header + result.join('\n');
}
