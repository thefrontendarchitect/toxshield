export function LegalSection({
  id,
  title,
  children,
}: {
  id: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section id={id} className="space-y-3">
      <h2 className="font-mono text-sm font-bold text-neon-cyan uppercase tracking-[0.15em] text-glow-subtle">
        {title}
      </h2>
      <div className="text-sm text-text-secondary leading-relaxed space-y-3">
        {children}
      </div>
    </section>
  );
}
