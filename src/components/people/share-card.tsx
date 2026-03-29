'use client';

import { useRef, useState } from 'react';
import html2canvas from 'html2canvas';
import { AnalysisRow } from '@/types/database';

interface ShareCardProps {
  analysis: AnalysisRow;
  personName: string;
}

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function resolveToken(token: string): string {
  if (typeof document === 'undefined') return '';
  return getComputedStyle(document.documentElement).getPropertyValue(token).trim();
}

export function ShareCard({ analysis, personName }: ShareCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState('');

  async function captureCard(): Promise<Blob | null> {
    if (!cardRef.current) return null;
    const bg = resolveToken('--color-surface-0') || '#080519';
    const canvas = await html2canvas(cardRef.current, {
      backgroundColor: bg,
      scale: 2,
      useCORS: true,
    });
    return new Promise((resolve) => canvas.toBlob(resolve, 'image/png'));
  }

  async function handleShare() {
    setExporting(true);
    setExportError('');
    try {
      const blob = await captureCard();
      if (!blob) return;

      const file = new File(
        [blob],
        `toxshield-${personName.toLowerCase().replace(/\s+/g, '-')}.png`,
        { type: 'image/png' }
      );

      if (navigator.share && navigator.canShare?.({ files: [file] })) {
        await navigator.share({
          title: `ToxShield: ${analysis.headline}`,
          text: analysis.tagline,
          files: [file],
        });
      } else {
        downloadBlob(blob, file.name);
      }
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') return;
      setExportError('Export failed. Please try again.');
    } finally {
      setExporting(false);
    }
  }

  async function handleDownload() {
    setExporting(true);
    setExportError('');
    try {
      const blob = await captureCard();
      if (blob) {
        downloadBlob(
          blob,
          `toxshield-${personName.toLowerCase().replace(/\s+/g, '-')}.png`
        );
      }
    } catch {
      setExportError('Download failed. Please try again.');
    } finally {
      setExporting(false);
    }
  }

  const traits = analysis.detected_traits ?? [];
  const isHigh = analysis.risk_level === 'high';
  const score = analysis.toxicity_score;

  // Resolve colors from CSS vars at render time (html2canvas captures inline styles)
  const ringColor = isHigh
    ? (resolveToken('--color-neon-magenta') || '#ff2878')
    : analysis.risk_level === 'moderate'
      ? (resolveToken('--color-warning-amber') || '#ffc832')
      : (resolveToken('--color-neon-cyan') || '#00b4ff');
  const bgColor = resolveToken('--color-surface-0') || '#080519';
  const textPrimary = resolveToken('--color-text-primary') || '#f0f6ff';
  const textSecondary = resolveToken('--color-text-secondary') || '#b8d4f0';
  const textMuted = '#6b8ab0';
  const accentCyan = resolveToken('--color-neon-cyan') || '#00b4ff';

  return (
    <div>
      {/* Capturable card — uses solid colors only (no backdrop-blur/filters for html2canvas) */}
      <div
        ref={cardRef}
        className="rounded-2xl p-6 space-y-5"
        style={{ backgroundColor: bgColor, border: `2px solid ${accentCyan}26` }}
      >
        {/* Header */}
        <div className="text-center space-y-1">
          <p
            className="font-mono uppercase tracking-[0.3em]"
            style={{ fontSize: '11px', color: textSecondary }}
          >
            ToxShield Analysis
          </p>
          {analysis.threat_type && (
            <p
              className="font-mono font-bold uppercase tracking-[0.15em]"
              style={{ fontSize: '10px', color: accentCyan }}
            >
              {analysis.threat_type}
            </p>
          )}
        </div>

        {/* Headline */}
        <div className="text-center">
          <h2
            className="font-mono font-bold uppercase"
            style={{ fontSize: '18px', color: textPrimary, lineHeight: '1.3' }}
          >
            &ldquo;{analysis.headline}&rdquo;
          </h2>
          <p
            className="font-mono italic mt-1"
            style={{ fontSize: '12px', color: textMuted }}
          >
            {analysis.tagline}
          </p>
        </div>

        {/* Score circle */}
        <div className="flex justify-center">
          <div
            className="flex items-center justify-center rounded-full font-mono font-bold"
            style={{
              width: '80px',
              height: '80px',
              border: `3px solid ${ringColor}`,
              color: textPrimary,
              fontSize: '28px',
              boxShadow: `0 0 20px ${ringColor}40, 0 0 40px ${ringColor}20`,
            }}
          >
            {score.toFixed(1)}
          </div>
        </div>

        {/* Trait pills */}
        <div className="flex flex-wrap justify-center gap-2">
          {traits.slice(0, 3).map((trait) => (
            <span
              key={trait.name}
              className="font-mono rounded-full"
              style={{
                fontSize: '11px',
                padding: '4px 12px',
                color: textSecondary,
                border: `1px solid ${accentCyan}33`,
                backgroundColor: `${accentCyan}14`,
              }}
            >
              {trait.name}
            </span>
          ))}
        </div>

        {/* CTA footer */}
        <p
          className="text-center font-mono"
          style={{ fontSize: '12px', color: textMuted }}
        >
          Analyze your circle &rarr; toxshield.in
        </p>
      </div>

      {/* Export error */}
      {exportError && (
        <p className="mt-2 text-center font-mono text-xs text-danger-red">{exportError}</p>
      )}

      {/* Action buttons */}
      <div className="mt-5 grid grid-cols-2 gap-3">
        <button
          type="button"
          onClick={handleShare}
          disabled={exporting}
          className="px-4 py-3.5 border border-neon-cyan/15 rounded-xl font-mono text-xs text-text-primary active:bg-neon-cyan/5 transition-colors text-center min-h-[48px] touch-active disabled:opacity-50"
        >
          {exporting ? 'Exporting...' : 'Share'}
        </button>
        <button
          type="button"
          onClick={handleDownload}
          disabled={exporting}
          className="px-4 py-3.5 bg-neon-cyan text-surface-0 font-bold rounded-xl font-mono text-xs active:bg-neon-cyan/90 transition-colors text-center min-h-[48px] touch-active disabled:opacity-50"
        >
          {exporting ? 'Exporting...' : 'Download Image'}
        </button>
      </div>
    </div>
  );
}
