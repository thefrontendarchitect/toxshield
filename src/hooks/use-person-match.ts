'use client';

import { useState, useCallback, useRef } from 'react';
import { generateQuirkyNames, type InputType } from '@/lib/utils/name-suggestions';
import type { MatchedPerson } from '@/types/database';

interface UsePersonMatchReturn {
  matchedPerson: MatchedPerson | null;
  isChecking: boolean;
  isDifferentPerson: boolean;
  suggestedNames: string[];
  selectedName: string | null;
  checkName: (name: string) => Promise<void>;
  markAsDifferent: (inputType: InputType, relationship?: string | null) => void;
  selectAlternateName: (name: string) => void;
  reset: () => void;
  /** The personId to send with the request (null = create new person) */
  resolvedPersonId: string | null;
  /** The name to send with the request (original or quirky alternate) */
  resolvedName: string | null;
}

export function usePersonMatch(): UsePersonMatchReturn {
  const [matchedPerson, setMatchedPerson] = useState<MatchedPerson | null>(null);
  const [isChecking, setIsChecking] = useState(false);
  const [isDifferentPerson, setIsDifferentPerson] = useState(false);
  const [suggestedNames, setSuggestedNames] = useState<string[]>([]);
  const [selectedName, setSelectedName] = useState<string | null>(null);
  const lastCheckedName = useRef<string>('');

  const checkName = useCallback(async (name: string) => {
    const trimmed = name.trim();
    if (!trimmed || trimmed === lastCheckedName.current) return;

    lastCheckedName.current = trimmed;
    setIsChecking(true);
    setMatchedPerson(null);
    setIsDifferentPerson(false);
    setSuggestedNames([]);
    setSelectedName(null);

    try {
      const res = await fetch(`/api/people/search?name=${encodeURIComponent(trimmed)}`);
      if (!res.ok) return;
      const data = (await res.json()) as { matches: MatchedPerson[] };
      if (data.matches?.length > 0) {
        setMatchedPerson(data.matches[0]);
      }
    } finally {
      setIsChecking(false);
    }
  }, []);

  const markAsDifferent = useCallback((inputType: InputType, relationship?: string | null) => {
    setIsDifferentPerson(true);
    if (matchedPerson) {
      setSuggestedNames(generateQuirkyNames(matchedPerson.name, inputType, relationship));
    }
  }, [matchedPerson]);

  const selectAlternateName = useCallback((name: string) => {
    setSelectedName(name);
  }, []);

  const reset = useCallback(() => {
    setMatchedPerson(null);
    setIsChecking(false);
    setIsDifferentPerson(false);
    setSuggestedNames([]);
    setSelectedName(null);
    lastCheckedName.current = '';
  }, []);

  // Determine what to send with the request
  const resolvedPersonId =
    matchedPerson && !isDifferentPerson ? matchedPerson.id : null;
  const resolvedName =
    isDifferentPerson && selectedName ? selectedName : null;

  return {
    matchedPerson,
    isChecking,
    isDifferentPerson,
    suggestedNames,
    selectedName,
    checkName,
    markAsDifferent,
    selectAlternateName,
    reset,
    resolvedPersonId,
    resolvedName,
  };
}
