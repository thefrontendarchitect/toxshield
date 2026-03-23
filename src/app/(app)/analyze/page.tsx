'use client';

import { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { RELATIONSHIP_OPTIONS } from '@/lib/constants';
import {
  parseWhatsAppExport,
  getParticipantSummaries,
  formatChatForAnalysis,
  type ParsedChat,
  type ParticipantSummary,
} from '@/lib/parsers/whatsapp';

type Mode = 'text' | 'chat';

export default function AnalyzePage() {
  const [mode, setMode] = useState<Mode>('text');

  return (
    <div>
      {/* Mode tabs */}
      <div className="flex items-center gap-1 mb-6 bg-white/5 rounded-xl p-1">
        {(['text', 'chat'] as Mode[]).map((m) => (
          <button
            key={m}
            onClick={() => setMode(m)}
            className={`flex-1 py-2.5 rounded-lg font-mono text-xs tracking-wider transition-all min-h-[40px] ${
              mode === m
                ? 'bg-white text-black font-bold'
                : 'text-white/40 active:bg-white/10'
            }`}
          >
            {m === 'text' ? 'DESCRIBE' : 'WHATSAPP'}
          </button>
        ))}
      </div>

      {mode === 'text' ? <TextMode /> : <ChatMode />}
    </div>
  );
}

/** Manual text description mode (existing behavior) */
function TextMode() {
  const [name, setName] = useState('');
  const [relationship, setRelationship] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, relationship: relationship || null, description }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Analysis failed');
      }

      const data = await response.json();
      router.push(`/people/${data.personId}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <p className="text-sm text-white/40 font-mono">
        Describe the subject. The more detail, the sharper the profile.
      </p>

      {error && (
        <div className="p-4 bg-white/10 border border-white/30 rounded-xl text-white text-sm font-mono font-bold">
          {error}
        </div>
      )}

      <div>
        <label className="block text-xs text-white/30 font-mono mb-1.5 uppercase tracking-wider">Subject Name</label>
        <input
          type="text" value={name} onChange={(e) => setName(e.target.value)}
          className="w-full px-4 py-3.5 bg-black border border-white/10 rounded-xl font-mono text-sm text-white placeholder:text-white/15 focus:outline-none focus:border-white/40 focus:ring-1 focus:ring-white/10 transition-colors min-h-[48px]"
          placeholder="Who are we analyzing?" required
        />
      </div>

      <div>
        <label className="block text-xs text-white/30 font-mono mb-1.5 uppercase tracking-wider">Relationship</label>
        <select
          value={relationship} onChange={(e) => setRelationship(e.target.value)}
          className="w-full px-4 py-3.5 bg-black border border-white/10 rounded-xl font-mono text-sm text-white focus:outline-none focus:border-white/40 focus:ring-1 focus:ring-white/10 transition-colors appearance-none min-h-[48px]"
        >
          <option value="">Select relationship...</option>
          {RELATIONSHIP_OPTIONS.map((opt) => (
            <option key={opt} value={opt.toLowerCase()}>{opt}</option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-xs text-white/30 font-mono mb-1.5 uppercase tracking-wider">Behavioral Description</label>
        <textarea
          value={description} onChange={(e) => setDescription(e.target.value)}
          className="w-full px-4 py-3.5 bg-black border border-white/10 rounded-xl font-mono text-sm text-white placeholder:text-white/15 focus:outline-none focus:border-white/40 focus:ring-1 focus:ring-white/10 transition-colors resize-none"
          rows={8} placeholder="Describe their behavior, specific incidents, how they make you feel..."
          required minLength={10}
        />
      </div>

      <button
        type="submit"
        disabled={loading || !name || !description || description.length < 10}
        className="w-full py-4 bg-white text-black font-bold rounded-xl font-mono text-sm tracking-wider active:bg-white/90 transition-all disabled:opacity-30 disabled:cursor-not-allowed min-h-[52px] touch-active"
      >
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <span className="inline-block w-4 h-4 border-2 border-black/20 border-t-black rounded-full animate-spin" />
            RUNNING ANALYSIS...
          </span>
        ) : 'INITIATE THREAT ANALYSIS →'}
      </button>

      {loading && (
        <div className="text-center font-mono text-xs text-white/30 space-y-1">
          <p>▸ Scanning behavioral patterns...</p>
          <p>▸ Cross-referencing manipulation frameworks...</p>
          <p>▸ Generating threat profile...</p>
        </div>
      )}
    </form>
  );
}

/** WhatsApp chat import mode */
function ChatMode() {
  const [parsedChat, setParsedChat] = useState<ParsedChat | null>(null);
  const [participants, setParticipants] = useState<ParticipantSummary[]>([]);
  const [selectedPerson, setSelectedPerson] = useState<string | null>(null);
  const [relationship, setRelationship] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [parseError, setParseError] = useState('');
  const fileRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setParseError('');
    setParsedChat(null);
    setSelectedPerson(null);

    try {
      const text = await file.text();
      const parsed = parseWhatsAppExport(text);

      if (parsed.participants.length === 0) {
        setParseError('No messages found. Make sure this is a WhatsApp chat export (.txt).');
        return;
      }

      setParsedChat(parsed);
      setParticipants(getParticipantSummaries(parsed));
    } catch {
      setParseError('Failed to parse chat. Make sure you exported without media.');
    }
  };

  const handleSubmit = async () => {
    if (!parsedChat || !selectedPerson) return;

    setError('');
    setLoading(true);

    try {
      const formatted = formatChatForAnalysis(
        selectedPerson,
        parsedChat.messagesByParticipant
      );

      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: selectedPerson,
          relationship: relationship || null,
          description: formatted,
          inputType: 'whatsapp_chat',
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Analysis failed');
      }

      const data = await response.json();
      router.push(`/people/${data.personId}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
      setLoading(false);
    }
  };

  const selectedSummary = participants.find((p) => p.name === selectedPerson);

  return (
    <div className="space-y-5">
      <p className="text-sm text-white/40 font-mono">
        Import a WhatsApp chat export to analyze someone based on their actual messages.
      </p>

      {/* Instructions */}
      <div className="bg-white/[0.03] border border-white/[0.06] rounded-xl p-4 space-y-2">
        <p className="text-xs text-white/50 font-mono font-bold">HOW TO EXPORT:</p>
        <div className="text-xs text-white/30 font-mono space-y-1">
          <p>1. Open the WhatsApp chat</p>
          <p>2. Tap ⋮ Menu → More → Export Chat</p>
          <p>3. Choose &quot;Without Media&quot;</p>
          <p>4. Save or share the .txt file</p>
        </div>
      </div>

      {/* File picker */}
      <div>
        <input
          ref={fileRef}
          type="file"
          accept=".txt,.text"
          onChange={handleFileSelect}
          className="hidden"
        />
        <button
          type="button"
          onClick={() => fileRef.current?.click()}
          className="w-full py-4 border-2 border-dashed border-white/15 rounded-xl font-mono text-sm text-white/50 active:bg-white/5 transition-colors min-h-[60px] touch-active"
        >
          {parsedChat
            ? `✓ ${parsedChat.totalMessages} messages from ${parsedChat.participants.length} people`
            : 'TAP TO SELECT CHAT EXPORT (.txt)'}
        </button>
      </div>

      {parseError && (
        <div className="p-4 bg-white/10 border border-white/30 rounded-xl text-white text-sm font-mono font-bold">
          {parseError}
        </div>
      )}

      {/* Participant picker */}
      {participants.length > 0 && (
        <div className="space-y-2">
          <label className="block text-xs text-white/30 font-mono uppercase tracking-wider">
            SELECT WHO TO ANALYZE
          </label>
          {participants.map((p) => {
            const isSelected = selectedPerson === p.name;
            const months = Math.max(
              1,
              Math.ceil(
                (p.lastMessage.getTime() - p.firstMessage.getTime()) /
                  (1000 * 60 * 60 * 24 * 30)
              )
            );

            return (
              <button
                key={p.name}
                type="button"
                onClick={() => setSelectedPerson(p.name)}
                className={`w-full flex items-center justify-between p-4 rounded-xl border transition-all touch-active min-h-[56px] text-left ${
                  isSelected
                    ? 'border-white bg-white/10'
                    : 'border-white/[0.06] bg-surface active:bg-hover'
                }`}
              >
                <div>
                  <p className={`font-mono text-sm ${isSelected ? 'text-white font-bold' : 'text-white/70'}`}>
                    {p.name}
                  </p>
                  <p className="text-xs text-white/30 font-mono mt-0.5">
                    {p.messageCount} messages · {months} month{months !== 1 ? 's' : ''}
                  </p>
                </div>
                {isSelected && <span className="text-white font-mono">●</span>}
              </button>
            );
          })}
        </div>
      )}

      {/* Relationship (after selecting person) */}
      {selectedPerson && (
        <div>
          <label className="block text-xs text-white/30 font-mono mb-1.5 uppercase tracking-wider">
            Relationship to {selectedPerson}
          </label>
          <select
            value={relationship}
            onChange={(e) => setRelationship(e.target.value)}
            className="w-full px-4 py-3.5 bg-black border border-white/10 rounded-xl font-mono text-sm text-white focus:outline-none focus:border-white/40 focus:ring-1 focus:ring-white/10 transition-colors appearance-none min-h-[48px]"
          >
            <option value="">Select relationship...</option>
            {RELATIONSHIP_OPTIONS.map((opt) => (
              <option key={opt} value={opt.toLowerCase()}>{opt}</option>
            ))}
          </select>
        </div>
      )}

      {/* Preview & submit */}
      {selectedSummary && (
        <>
          <div className="bg-white/[0.03] border border-white/[0.06] rounded-xl p-4 text-center">
            <p className="text-xs text-white/50 font-mono">
              Analyzing <span className="text-white font-bold">{selectedSummary.messageCount}</span> messages
              from <span className="text-white font-bold">{selectedPerson}</span>
              {parsedChat?.dateRange && (
                <>
                  {' '}over{' '}
                  <span className="text-white/70">
                    {parsedChat.dateRange.from.toLocaleDateString()} — {parsedChat.dateRange.to.toLocaleDateString()}
                  </span>
                </>
              )}
            </p>
          </div>

          {error && (
            <div className="p-4 bg-white/10 border border-white/30 rounded-xl text-white text-sm font-mono font-bold">
              {error}
            </div>
          )}

          <button
            type="button"
            onClick={handleSubmit}
            disabled={loading}
            className="w-full py-4 bg-white text-black font-bold rounded-xl font-mono text-sm tracking-wider active:bg-white/90 transition-all disabled:opacity-30 disabled:cursor-not-allowed min-h-[52px] touch-active"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="inline-block w-4 h-4 border-2 border-black/20 border-t-black rounded-full animate-spin" />
                ANALYZING CHAT PATTERNS...
              </span>
            ) : (
              'ANALYZE CHAT →'
            )}
          </button>

          {loading && (
            <div className="text-center font-mono text-xs text-white/30 space-y-1">
              <p>▸ Reading conversation patterns...</p>
              <p>▸ Detecting manipulation tactics...</p>
              <p>▸ Building behavioral profile...</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
