export function Spinner({ className }: { className?: string }) {
  return (
    <span
      role="status"
      aria-label="Loading"
      className={`inline-block w-4 h-4 border-2 border-black/20 border-t-black rounded-full animate-spin ${className ?? ''}`}
    />
  );
}
