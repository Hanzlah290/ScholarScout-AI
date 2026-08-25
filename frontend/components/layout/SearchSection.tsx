interface SearchSectionProps {
  value: string;
  onChange: (value: string) => void;
}

export default function SearchSection({
  value,
  onChange,
}: SearchSectionProps) {
  return (
    <section>
      <input
        type="text"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Search scholarships..."
        className="w-full rounded-lg border bg-background px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-ring"
      />
    </section>
  );
}