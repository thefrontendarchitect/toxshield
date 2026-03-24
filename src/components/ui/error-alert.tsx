export function ErrorAlert({ message }: { message: string }) {
  return (
    <div className="p-4 bg-white/10 border border-white/30 rounded-xl text-white text-sm font-mono font-bold">
      {message}
    </div>
  );
}
