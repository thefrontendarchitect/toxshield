export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col min-h-screen bg-surface-0">
      <main className="flex-1 flex items-center justify-center p-4">
        {children}
      </main>
    </div>
  );
}
