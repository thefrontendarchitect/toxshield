import { ReactNode } from 'react';

interface PageContainerProps {
  children: ReactNode;
  className?: string;
  withBottomNav?: boolean;
  withDetailFooter?: boolean;
}

export function PageContainer({
  children,
  className = '',
  withBottomNav = false,
  withDetailFooter = false,
}: PageContainerProps) {
  const bottomPadding = withBottomNav
    ? 'calc(80px + var(--safe-bottom-reduced, 0px))'
    : withDetailFooter
      ? 'calc(120px + var(--safe-bottom-reduced, 0px))'
      : undefined;

  return (
    <div
      className={`min-h-screen bg-surface-0 pt-[calc(56px+var(--safe-top,0px))] ${className}`}
      style={bottomPadding ? { paddingBottom: bottomPadding } : undefined}
    >
      {children}
    </div>
  );
}
