export function ErrorAlert({ message }: { message: string }) {
  return (
    <div className="p-4 bg-neon-cyan/10 border border-neon-cyan/30 rounded-xl text-text-primary text-sm font-mono font-bold">
      {message}
    </div>
  );
}
