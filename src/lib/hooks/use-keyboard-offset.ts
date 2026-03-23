'use client';

import { useEffect } from 'react';

/**
 * Sets `--keyboard-height` CSS variable based on the Visual Viewport API.
 *
 * On Android (adjustPan): window.innerHeight stays fixed while
 * visualViewport.height shrinks when the keyboard opens.
 *
 * On iOS (resize: 'native'): Both values shrink together, so
 * the difference is 0 — iOS already repositions fixed elements.
 *
 * On desktop/web: visualViewport matches innerHeight — no offset.
 */
export function useKeyboardOffset() {
  useEffect(() => {
    const vv = window.visualViewport;
    if (!vv) return;

    function update() {
      const keyboardHeight = Math.max(0, window.innerHeight - vv!.height);
      document.documentElement.style.setProperty(
        '--keyboard-height',
        `${keyboardHeight}px`
      );
    }

    vv.addEventListener('resize', update);
    vv.addEventListener('scroll', update);

    return () => {
      vv.removeEventListener('resize', update);
      vv.removeEventListener('scroll', update);
      document.documentElement.style.setProperty('--keyboard-height', '0px');
    };
  }, []);
}
