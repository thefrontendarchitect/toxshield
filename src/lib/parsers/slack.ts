import { unzipSync } from 'fflate';

interface SlackMessage {
  date: Date;
  message: string;
}

export interface SlackParsedChat {
  participants: string[];
  messagesByParticipant: Record<string, SlackMessage[]>;
  totalMessages: number;
  dateRange: { from: Date; to: Date } | null;
}

export interface SlackParticipantSummary {
  name: string;
  messageCount: number;
  firstMessage: Date;
  lastMessage: Date;
}

interface SlackExportData {
  channels: string[];
  usersMap: Record<string, string>;
  rawFiles: Record<string, Uint8Array>;
}

interface SlackJsonMessage {
  type?: string;
  subtype?: string;
  user?: string;
  text?: string;
  ts?: string;
}

interface SlackUser {
  id: string;
  name: string;
  real_name?: string;
  profile?: { display_name?: string; real_name?: string };
}

const SKIP_SUBTYPES = new Set([
  'channel_join',
  'channel_leave',
  'channel_topic',
  'channel_purpose',
  'channel_name',
  'channel_archive',
  'channel_unarchive',
  'bot_message',
  'pinned_item',
  'unpinned_item',
  'file_comment',
  'me_message',
  'reminder_add',
  'tombstone',
  'thread_broadcast',
]);

/**
 * Parse a Slack workspace export ZIP.
 * Returns the list of channels, a user ID → display name map, and raw file data.
 */
export function parseSlackExport(zipBuffer: ArrayBuffer): SlackExportData {
  const files = unzipSync(new Uint8Array(zipBuffer));

  // Build user map from users.json
  const usersMap: Record<string, string> = {};
  const usersFile = Object.entries(files).find(([name]) =>
    name === 'users.json' || name.endsWith('/users.json')
  );

  if (usersFile) {
    try {
      const users: SlackUser[] = JSON.parse(new TextDecoder().decode(usersFile[1]));
      for (const user of users) {
        const displayName =
          user.profile?.display_name ||
          user.profile?.real_name ||
          user.real_name ||
          user.name;
        usersMap[user.id] = displayName;
      }
    } catch {
      // users.json parse failed — we'll fall back to raw IDs
    }
  }

  // Discover channels: directories containing .json message files (not users.json/channels.json/etc.)
  const channelSet = new Set<string>();
  const topLevelFiles = new Set(['users.json', 'channels.json', 'integration_logs.json', 'dms.json', 'groups.json', 'mpims.json']);

  for (const name of Object.keys(files)) {
    const parts = name.split('/');
    // Channel files look like: channel-name/2024-01-01.json
    if (parts.length >= 2 && name.endsWith('.json')) {
      const channelName = parts[parts.length - 2];
      const fileName = parts[parts.length - 1];
      if (!topLevelFiles.has(fileName) && !topLevelFiles.has(name)) {
        channelSet.add(channelName);
      }
    }
  }

  const channels = Array.from(channelSet).sort();

  return { channels, usersMap, rawFiles: files };
}

/**
 * Parse messages from a specific channel in the Slack export.
 */
export function parseSlackChannel(
  rawFiles: Record<string, Uint8Array>,
  channel: string,
  usersMap: Record<string, string>
): SlackParsedChat {
  const messagesByParticipant: Record<string, SlackMessage[]> = {};
  let totalMessages = 0;
  let earliest: Date | null = null;
  let latest: Date | null = null;

  // Find all JSON files for this channel
  const channelFiles = Object.entries(rawFiles)
    .filter(([name]) => {
      const parts = name.split('/');
      return parts.length >= 2 && parts[parts.length - 2] === channel && name.endsWith('.json');
    })
    .sort(([a], [b]) => a.localeCompare(b)); // sort by date filename

  for (const [, fileData] of channelFiles) {
    let messages: SlackJsonMessage[];
    try {
      messages = JSON.parse(new TextDecoder().decode(fileData));
    } catch {
      continue;
    }

    if (!Array.isArray(messages)) continue;

    for (const msg of messages) {
      // Skip non-message types and system subtypes
      if (msg.type !== 'message') continue;
      if (msg.subtype && SKIP_SUBTYPES.has(msg.subtype)) continue;
      if (!msg.user || !msg.text) continue;

      const author = usersMap[msg.user] || msg.user;
      const text = cleanSlackMarkdown(msg.text, usersMap);
      const date = new Date(parseFloat(msg.ts || '0') * 1000);

      if (isNaN(date.getTime())) continue;

      totalMessages++;

      if (!messagesByParticipant[author]) {
        messagesByParticipant[author] = [];
      }

      messagesByParticipant[author].push({ date, message: text });

      if (!earliest || date < earliest) earliest = date;
      if (!latest || date > latest) latest = date;
    }
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
 * Clean Slack mrkdwn formatting for readable analysis.
 */
function cleanSlackMarkdown(text: string, usersMap: Record<string, string>): string {
  return text
    // Replace user mentions <@U12345> with display names
    .replace(/<@(U[A-Z0-9]+)>/g, (_, id) => `@${usersMap[id] || id}`)
    // Replace channel mentions <#C12345|channel-name>
    .replace(/<#[A-Z0-9]+\|([^>]+)>/g, '#$1')
    // Replace URL links <url|label>
    .replace(/<(https?:\/\/[^|>]+)\|([^>]+)>/g, '$2')
    // Replace bare URL links <url>
    .replace(/<(https?:\/\/[^>]+)>/g, '$1')
    // Decode HTML entities
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");
}

/**
 * Get summary info for each participant (for the picker UI).
 */
export function getParticipantSummaries(parsed: SlackParsedChat): SlackParticipantSummary[] {
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
 * Format Slack messages for AI analysis.
 * Uses the same strategy as WhatsApp: 80% recent + 20% early, with [TARGET] markers.
 */
export function formatSlackForAnalysis(
  targetPerson: string,
  allParticipantMessages: Record<string, SlackMessage[]>,
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
  const earlyBudget = Math.floor(maxChars * 0.2);
  const recentBudget = maxChars - earlyBudget;

  // Recent messages (last 80% of budget)
  for (let i = formatted.length - 1; i >= 0; i--) {
    const line = formatted[i];
    if (currentChars + line.length + 1 > recentBudget) break;
    result.unshift(line);
    currentChars += line.length + 1;
  }

  // Early messages (first 20% of budget)
  const hasRecentMessages = result.length > 0;
  if (hasRecentMessages && formatted.length > result.length + 10) {
    const earlyMessages: string[] = [];
    let earlyChars = 0;

    for (let i = 0; i < formatted.length; i++) {
      if (result[0] === formatted[i]) break;
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

  const header = `Slack conversation analysis — Target: ${targetPerson}
Total messages from ${targetPerson}: ${targetMsgCount}
Messages shown: ${totalIncluded} of ${allMessages.length}
${allMessages.length > 0 ? `Date range: ${allMessages[0].date.toLocaleDateString()} → ${allMessages[allMessages.length - 1].date.toLocaleDateString()}` : ''}
---
`;

  return header + result.join('\n');
}
