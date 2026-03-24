'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { RELATIONSHIP_OPTIONS } from '@/lib/constants';
import {
  parseWhatsAppExport,
  extractWhatsAppZip,
  getParticipantSummaries,
  formatChatForAnalysis,
  type ParsedChat,
  type ParticipantSummary,
} from '@/lib/parsers/whatsapp';
import { FormSelect } from '@/components/ui/form-input';
import { ErrorAlert } from '@/components/ui/error-alert';
import { Spinner } from '@/components/ui/spinner';
import { PersonMatchBanner } from '@/components/ui/person-match-banner';
import { usePersonMatch } from '@/hooks/use-person-match';
import { AnalysisResult } from '@/types/analysis';

interface ChatModeFormProps {
  apiEndpoint?: string;
  onResult?: (name: string, relationship: string | null, result: AnalysisResult) => void;
}

export function ChatModeForm({ apiEndpoint = '/api/analyze', onResult }: ChatModeFormProps) {
  const [parsedChat, setParsedChat] = useState<ParsedChat | null>(null);
  const [participants, setParticipants] = useState<ParticipantSummary[]>([]);
  const [selectedPerson, setSelectedPerson] = useState<string | null>(null);
  const [relationship, setRelationship] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [parseError, setParseError] = useState('');
  const fileRef = useRef<HTMLInputElement>(null);
  const router = useRouter();
  const personMatch = usePersonMatch();

  // Check for existing person when participant is selected
  useEffect(() => {
    if (selectedPerson && apiEndpoint === '/api/analyze') {
      personMatch.checkName(selectedPerson);
    } else {
      personMatch.reset();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedPerson]);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setParseError('');
    setParsedChat(null);
    setSelectedPerson(null);

    try {
      let text: string;
      if (file.name.endsWith('.zip')) {
        const buffer = await file.arrayBuffer();
        text = extractWhatsAppZip(buffer);
      } else {
        text = await file.text();
      }
      const parsed = parseWhatsAppExport(text);

      if (parsed.participants.length === 0) {
        setParseError('No messages found. Make sure this is a WhatsApp chat export (.txt or .zip).');
        return;
      }

      setParsedChat(parsed);
      setParticipants(getParticipantSummaries(parsed));
    } catch {
      setParseError('Failed to parse chat. Make sure this is a valid WhatsApp export (.txt or .zip).');
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

      const submitName = personMatch.resolvedName || selectedPerson;
      const response = await fetch(apiEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: submitName,
          relationship: relationship || null,
          description: formatted,
          inputType: 'whatsapp_chat',
          ...(personMatch.resolvedPersonId && { personId: personMatch.resolvedPersonId }),
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Analysis failed');
      }

      const data = await response.json();

      if (onResult) {
        onResult(selectedPerson, relationship || null, data.result);
        setParsedChat(null);
        setParticipants([]);
        setSelectedPerson(null);
        setRelationship('');
        personMatch.reset();
        setLoading(false);
      } else {
        router.push(`/people/${data.personId}`);
      }
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
          accept=".txt,.text,.zip"
          onChange={handleFileSelect}
          className="hidden"
          aria-label="Select WhatsApp chat export file"
        />
        <button
          type="button"
          onClick={() => fileRef.current?.click()}
          className="w-full py-4 border-2 border-dashed border-white/15 rounded-xl font-mono text-sm text-white/50 active:bg-white/5 transition-colors min-h-[60px] touch-active"
        >
          {parsedChat
            ? `✓ ${parsedChat.totalMessages} messages from ${parsedChat.participants.length} people`
            : 'TAP TO SELECT CHAT EXPORT (.txt or .zip)'}
        </button>
      </div>

      {parseError && <ErrorAlert message={parseError} />}

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

      {/* Person match detection */}
      {selectedPerson && apiEndpoint === '/api/analyze' && personMatch.matchedPerson && (
        <PersonMatchBanner
          matchedPerson={personMatch.matchedPerson}
          isChecking={personMatch.isChecking}
          isDifferentPerson={personMatch.isDifferentPerson}
          suggestedNames={personMatch.suggestedNames}
          selectedName={personMatch.selectedName}
          inputType="whatsapp_chat"
          relationship={relationship}
          onMarkDifferent={personMatch.markAsDifferent}
          onSelectName={personMatch.selectAlternateName}
        />
      )}

      {/* Relationship (after selecting person) */}
      {selectedPerson && (
        <FormSelect
          label={`Relationship to ${selectedPerson}`}
          id="chat-relationship"
          value={relationship}
          onChange={(e) => setRelationship(e.target.value)}
        >
          <option value="">Select relationship...</option>
          {RELATIONSHIP_OPTIONS.map((opt) => (
            <option key={opt} value={opt.toLowerCase()}>{opt}</option>
          ))}
        </FormSelect>
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

          {error && <ErrorAlert message={error} />}

          <button
            type="button"
            onClick={handleSubmit}
            disabled={loading || (personMatch.isDifferentPerson && !personMatch.selectedName)}
            className="w-full py-4 bg-white text-background font-bold rounded-xl font-mono text-sm tracking-wider active:bg-white/90 transition-all disabled:opacity-30 disabled:cursor-not-allowed min-h-[52px] touch-active"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <Spinner />
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
