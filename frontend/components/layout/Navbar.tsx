export default function Navbar() {
  return (
    <header className="flex flex-col gap-2 rounded-lg border p-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 className="text-xl font-semibold">🎓 ScholarScout AI</h1>
        <p className="text-sm text-muted-foreground">
          China Scholarship Dashboard
        </p>
      </div>

      <div className="text-sm text-muted-foreground">
        Last Scan: --
      </div>
    </header>
  );
}