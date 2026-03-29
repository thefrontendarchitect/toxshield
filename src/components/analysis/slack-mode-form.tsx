'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { RELATIONSHIP_OPTIONS } from '@/lib/constants';
import {
  parseSlackExport,
  parseSlackChannel,
  getParticipantSummaries,
  formatSlackForAnalysis,
  type SlackParsedChat,
  type SlackParticipantSummary,
} from '@/lib/parsers/slack';
import { FormSelect } from '@/components/ui/form-input';
import { ErrorAlert } from '@/components/ui/error-alert';
import { Spinner } from '@/components/ui/spinner';
import { PersonMatchBanner } from '@/components/ui/person-match-banner';
import { usePersonMatch } from '@/hooks/use-person-match';
import { AnalysisResult } from '@/types/analysis';

interface SlackModeFormProps {
  apiEndpoint?: string;
  onResult?: (name: string, relationship: string | null, result: AnalysisResult) => void;
}

export function SlackModeForm({ apiEndpoint = '/api/analyze', onResult }: SlackModeFormProps) {
  const [zipData, setZipData] = useState<{
    channels: string[];
    usersMap: Record<string, string>;
    rawFiles: Record<string, Uint8Array>;
  } | null>(null);
  const [selectedChannel, setSelectedChannel] = useState<string | null>(null);
  const [parsedChat, setParsedChat] = useState<SlackParsedChat | null>(null);
  const [participants, setParticipants] = useState<SlackParticipantSummary[]>([]);
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
    setZipData(null);
    setSelectedChannel(null);
    setParsedChat(null);
    setSelectedPerson(null);

    try {
      const buffer = await file.arrayBuffer();
      const data = parseSlackExport(buffer);

      if (data.channels.length === 0) {
        setParseError('No channels found. Make sure this is a Slack workspace export (.zip).');
        return;
      }

      setZipData(data);
    } catch {
      setParseError('Failed to parse export. Make sure this is a valid Slack workspace export (.zip).');
    }
  };

  const handleChannelSelect = (channel: string) => {
    if (!zipData) return;

    setSelectedChannel(channel);
    setSelectedPerson(null);
    setParsedChat(null);

    try {
      const parsed = parseSlackChannel(zipData.rawFiles, channel, zipData.usersMap);

      if (parsed.participants.length === 0) {
        setParseError(`No messages found in #${channel}.`);
        return;
      }

      setParseError('');
      setParsedChat(parsed);
      setParticipants(getParticipantSummaries(parsed));
    } catch {
      setParseError(`Failed to parse messages in #${channel}.`);
    }
  };

  const handleSubmit = async () => {
    if (!parsedChat || !selectedPerson) return;

    setError('');
    setLoading(true);

    try {
      const formatted = formatSlackForAnalysis(
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
          inputType: 'slack_chat',
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
        setZipData(null);
        setSelectedChannel(null);
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
      <p className="label-section mb-1">
        IMPORT A SLACK WORKSPACE EXPORT TO ANALYZE WORKPLACE MESSAGES.
      </p>

      {/* Instructions */}
      <div className="card-dashed space-y-2">
        <p className="font-mono text-[10px] font-bold text-text-secondary uppercase tracking-wider">HOW TO EXPORT:</p>
        <div className="font-mono text-[10px] text-text-secondary space-y-1">
          <p>1. Go to your Slack workspace settings</p>
          <p>2. Import/Export Data → Export</p>
          <p>3. Select date range and start export</p>
          <p>4. Download the .zip file when ready</p>
        </div>
      </div>

      {/* File picker */}
      <div>
        <input
          ref={fileRef}
          type="file"
          accept=".zip"
          onChange={handleFileSelect}
          className="hidden"
          aria-label="Select Slack workspace export file"
        />
        <button
          type="button"
          onClick={() => fileRef.current?.click()}
          className="w-full py-4 border border-dashed border-surface-3 rounded-lg font-mono text-xs text-text-secondary uppercase tracking-wider active:bg-surface-2 transition-colors min-h-[60px] touch-active"
        >
          {zipData
            ? `✓ ${zipData.channels.length} channel${zipData.channels.length !== 1 ? 's' : ''} found`
            : 'TAP TO SELECT SLACK EXPORT (.zip)'}
        </button>
      </div>

      {parseError && <ErrorAlert message={parseError} />}

      {/* Channel picker */}
      {zipData && zipData.channels.length > 0 && (
        <div className="space-y-2">
          <p className="label-section mb-2">
            SELECT CHANNEL
          </p>
          <div className="max-h-[240px] overflow-y-auto space-y-1.5">
            {zipData.channels.map((ch) => {
              const isSelected = selectedChannel === ch;

              return (
                <button
                  key={ch}
                  type="button"
                  onClick={() => handleChannelSelect(ch)}
                  className={`w-full flex items-center justify-between p-3.5 rounded-lg border transition-all touch-active min-h-[48px] text-left ${
                    isSelected
                      ? 'border-neon-cyan bg-neon-cyan/10'
                      : 'border-surface-3 bg-surface-1 active:bg-surface-2'
                  }`}
                >
                  <p className={`font-mono text-sm ${isSelected ? 'text-text-primary font-bold' : 'text-text-secondary'}`}>
                    #{ch}
                  </p>
                  {isSelected && <span className="text-neon-cyan font-mono">●</span>}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Participant picker */}
      {participants.length > 0 && (
        <div className="space-y-2">
          <p className="label-section mb-2">
            SELECT WHO TO ANALYZE
          </p>
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
                className={`w-full flex items-center justify-between p-4 rounded-lg border transition-all touch-active min-h-[56px] text-left ${
                  isSelected
                    ? 'border-neon-cyan bg-neon-cyan/10'
                    : 'border-surface-3 bg-surface-1 active:bg-surface-2'
                }`}
              >
                <div>
                  <p className={`font-mono text-sm ${isSelected ? 'text-text-primary font-bold' : 'text-text-secondary'}`}>
                    {p.name}
                  </p>
                  <p className="text-xs text-text-secondary font-mono mt-0.5">
                    {p.messageCount} messages · {months} month{months !== 1 ? 's' : ''}
                  </p>
                </div>
                {isSelected && <span className="text-neon-cyan font-mono">●</span>}
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
          inputType="slack_chat"
          relationship={relationship}
          onMarkDifferent={personMatch.markAsDifferent}
          onSelectName={personMatch.selectAlternateName}
        />
      )}

      {/* Relationship (after selecting person) */}
      {selectedPerson && (
        <FormSelect
          label={`Relationship to ${selectedPerson}`}
          id="slack-relationship"
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
          <div className="card-dashed text-center">
            <p className="text-xs text-text-secondary font-mono">
              Analyzing <span className="text-text-primary font-bold">{selectedSummary.messageCount}</span> messages
              from <span className="text-text-primary font-bold">{selectedPerson}</span>
              {selectedChannel && (
                <>
                  {' '}in <span className="text-text-primary">#{selectedChannel}</span>
                </>
              )}
              {parsedChat?.dateRange && (
                <>
                  {' '}over{' '}
                  <span className="text-text-primary">
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
            className="w-full py-4 bg-neon-cyan text-surface-0 font-bold rounded-lg font-mono text-xs uppercase tracking-[0.15em] active:bg-neon-cyan/90 transition-all disabled:opacity-30 disabled:cursor-not-allowed min-h-[52px] touch-active"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <Spinner />
                ANALYZING WORKPLACE PATTERNS...
              </span>
            ) : (
              'ANALYZE SLACK MESSAGES \u2192'
            )}
          </button>

          {loading && (
            <div className="text-center font-mono text-[10px] text-text-secondary uppercase tracking-wider space-y-1">
              <p>&gt;&gt; Reading workplace communication patterns...</p>
              <p>&gt;&gt; Detecting office manipulation tactics...</p>
              <p>&gt;&gt; Building professional behavioral profile...</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
