'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { WrappedData } from '@/lib/utils/wrapped';

export default function WrappedPage() {
  const [data, setData] = useState<WrappedData | null>(null);
  const [month, setMonth] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [slideIndex, setSlideIndex] = useState(0);

  useEffect(() => {
    fetch('/api/wrapped')
      .then((r) => r.json())
      .then((d) => {
        setData(d.wrapped);
        setMonth(d.month);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <p className="font-mono text-xs text-text-secondary animate-pulse">GENERATING YOUR WRAPPED...</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-4">
        <p className="font-mono text-lg text-text-primary">No data for {month}</p>
        <p className="font-mono text-xs text-text-secondary">Complete some analyses to unlock your Wrapped.</p>
      </div>
    );
  }

  const slides = buildSlides(data);
  const totalSlides = slides.length;

  const goNext = () => setSlideIndex((i) => Math.min(i + 1, totalSlides - 1));
  const goPrev = () => setSlideIndex((i) => Math.max(i - 1, 0));

  return (
    <div className="min-h-[70vh] flex flex-col">
      {/* Slide content */}
      <button type="button" onClick={goNext} aria-label="Advance to next slide" className="flex-1 flex items-center justify-center px-2 focus:outline-none cursor-default">
        <AnimatePresence mode="wait">
          <motion.div
            key={slideIndex}
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -40 }}
            transition={{ duration: 0.4 }}
            className="w-full max-w-sm text-center space-y-6 py-8"
          >
            {slides[slideIndex]}
          </motion.div>
        </AnimatePresence>
      </button>

      {/* Progress dots + nav */}
      <div className="pb-4 space-y-3">
        <div className="flex justify-center gap-1.5">
          {slides.map((_, i) => (
            <button
              key={i}
              type="button"
              onClick={() => setSlideIndex(i)}
              className={`w-2 h-2 rounded-full transition-all ${
                i === slideIndex ? 'bg-neon-cyan w-6' : 'bg-surface-3'
              }`}
              aria-label={`Go to slide ${i + 1}`}
            />
          ))}
        </div>
        <div className="flex justify-center gap-4">
          <button
            type="button"
            onClick={goPrev}
            disabled={slideIndex === 0}
            className="font-mono text-xs text-text-secondary disabled:opacity-20 active:text-neon-cyan touch-active px-4 py-2"
          >
            &larr; PREV
          </button>
          <button
            type="button"
            onClick={goNext}
            disabled={slideIndex === totalSlides - 1}
            className="font-mono text-xs text-text-secondary disabled:opacity-20 active:text-neon-cyan touch-active px-4 py-2"
          >
            NEXT &rarr;
          </button>
        </div>
      </div>
    </div>
  );
}

function buildSlides(data: WrappedData): React.ReactNode[] {
  const slides: React.ReactNode[] = [];

  // Slide 1: Intro
  slides.push(
    <div key="intro" className="space-y-4">
      <p className="font-mono text-[10px] text-neon-cyan/40 uppercase tracking-[0.3em]">ToxShield Wrapped</p>
      <h1 className="font-mono text-3xl font-black italic text-text-primary">{data.month}</h1>
      <p className="font-mono text-xs text-text-secondary">Your forensic intelligence report is ready.</p>
      <p className="font-mono text-[10px] text-neon-cyan/30 mt-8 animate-pulse">TAP TO CONTINUE &rarr;</p>
    </div>
  );

  // Slide 2: Volume
  slides.push(
    <div key="volume" className="space-y-4">
      <p className="font-mono text-[10px] text-neon-cyan/40 uppercase tracking-[0.2em]">This Month</p>
      <p className="font-mono text-6xl font-black italic text-text-primary text-glow-subtle">
        {data.totalAnalyses}
      </p>
      <p className="font-mono text-sm text-text-secondary">
        {data.totalAnalyses === 1 ? 'analysis performed' : 'analyses performed'}
      </p>
      <p className="font-mono text-xs text-neon-cyan/60">
        across {data.totalPeopleAnalyzed} {data.totalPeopleAnalyzed === 1 ? 'person' : 'people'}
      </p>
    </div>
  );

  // Slide 3: Hottest Profile
  if (data.highestScoringPerson) {
    slides.push(
      <div key="hottest" className="space-y-4">
        <p className="font-mono text-[10px] text-neon-magenta/60 uppercase tracking-[0.2em]">Highest Threat</p>
        <p className="font-mono text-4xl font-black italic text-neon-magenta text-glow-magenta">
          {data.highestScoringPerson.score.toFixed(1)}
        </p>
        <p className="font-mono text-lg font-bold text-text-primary uppercase">
          &ldquo;{data.highestScoringPerson.headline}&rdquo;
        </p>
        {data.highestScoringPerson.threatType && (
          <span className="inline-block px-4 py-1.5 border border-neon-magenta/20 rounded-full font-mono text-[10px] font-bold uppercase tracking-[0.15em] text-neon-magenta">
            {data.highestScoringPerson.threatType}
          </span>
        )}
        <p className="font-mono text-xs text-text-secondary">{data.highestScoringPerson.name}</p>
      </div>
    );
  }

  // Slide 4: Top Trait
  if (data.mostCommonTrait) {
    slides.push(
      <div key="trait" className="space-y-4">
        <p className="font-mono text-[10px] text-neon-cyan/40 uppercase tracking-[0.2em]">Most Detected Pattern</p>
        <p className="font-mono text-2xl font-black italic text-neon-cyan text-glow-subtle">
          {data.mostCommonTrait.name}
        </p>
        <p className="font-mono text-sm text-text-secondary">
          Detected {data.mostCommonTrait.count} {data.mostCommonTrait.count === 1 ? 'time' : 'times'}
        </p>
        <p className="font-mono text-xs text-text-secondary/60">
          {data.totalTraitsDetected} total traits identified
        </p>
      </div>
    );
  }

  // Slide 5: Risk Distribution
  slides.push(
    <div key="risk" className="space-y-4">
      <p className="font-mono text-[10px] text-neon-cyan/40 uppercase tracking-[0.2em]">Risk Breakdown</p>
      <div className="space-y-3 w-full max-w-[240px] mx-auto">
        {[
          { label: 'HIGH', value: data.riskDistribution.high, color: 'bg-neon-magenta', textColor: 'text-neon-magenta' },
          { label: 'MODERATE', value: data.riskDistribution.moderate, color: 'bg-warning-amber', textColor: 'text-warning-amber' },
          { label: 'LOW', value: data.riskDistribution.low, color: 'bg-neon-cyan', textColor: 'text-neon-cyan' },
        ].map((r) => {
          const pct = data.totalAnalyses > 0 ? (r.value / data.totalAnalyses) * 100 : 0;
          return (
            <div key={r.label} className="flex items-center gap-3">
              <span className={`font-mono text-[10px] w-16 text-right ${r.textColor}`}>{r.label}</span>
              <div className="flex-1 h-3 bg-surface-2 rounded-full overflow-hidden">
                <div className={`h-full ${r.color} rounded-full transition-all`} style={{ width: `${pct}%` }} />
              </div>
              <span className="font-mono text-xs text-text-secondary w-6">{r.value}</span>
            </div>
          );
        })}
      </div>
    </div>
  );

  // Slide 6: Boundary Trend
  slides.push(
    <div key="boundary" className="space-y-4">
      <p className="font-mono text-[10px] text-neon-cyan/40 uppercase tracking-[0.2em]">Your Boundaries</p>
      <p className={`font-mono text-2xl font-black italic ${
        data.boundaryTrend === 'Strengthening' ? 'text-neon-mint' :
        data.boundaryTrend === 'Needs Work' ? 'text-warning-amber' :
        'text-neon-cyan'
      }`}>
        {data.boundaryTrend}
      </p>
      <p className="font-mono text-xs text-text-secondary">
        {data.boundaryTrend === 'Strengthening'
          ? 'Your boundary awareness is improving. Keep it up.'
          : data.boundaryTrend === 'Needs Work'
            ? 'Some patterns suggest your boundaries could use reinforcement.'
            : 'Your boundaries are holding steady. Consistency matters.'}
      </p>
    </div>
  );

  // Slide 7: Summary
  slides.push(
    <div key="summary" className="space-y-4">
      <p className="font-mono text-[10px] text-neon-cyan/40 uppercase tracking-[0.3em]">Summary</p>
      <p className="font-mono text-lg font-bold text-text-primary">
        {data.totalAnalyses} analyses. {data.totalPeopleAnalyzed} people. {data.totalTraitsDetected} traits detected.
      </p>
      <p className="font-mono text-sm text-text-secondary">
        Average toxicity across your circle: <span className="text-neon-cyan font-bold">{data.averageToxicityScore}/10</span>
      </p>
      {data.topThreatTypes.length > 0 && (
        <div className="flex flex-wrap justify-center gap-2 mt-2">
          {data.topThreatTypes.map((t) => (
            <span key={t} className="px-3 py-1 border border-neon-cyan/15 rounded-full font-mono text-[10px] text-neon-cyan">
              {t}
            </span>
          ))}
        </div>
      )}
      <p className="font-mono text-[10px] text-text-secondary/40 mt-6">
        toxshield.in
      </p>
    </div>
  );

  return slides;
}
