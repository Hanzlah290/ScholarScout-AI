import ScholarshipCard from "@/components/scholarships/ScholarshipCard";
import type { Scholarship } from "@/types/scholarship";

interface ScholarshipListProps {
  scholarships: Scholarship[];
}

export default function ScholarshipList({
  scholarships,
}: ScholarshipListProps) {
  if (scholarships.length === 0) {
    return (
      <div className="rounded-lg border p-6 text-center text-muted-foreground">
        No scholarships found.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
      {scholarships.map((scholarship) => (
        <ScholarshipCard
          key={scholarship.id}
          scholarship={scholarship}
        />
      ))}
    </div>
  );
}
