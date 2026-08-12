import ScholarshipList from "@/components/scholarships/ScholarshipList";
import type { Scholarship } from "@/types/scholarship";

interface ContentSectionProps {
  scholarships: Scholarship[];
}

export default function ContentSection({
  scholarships,
}: ContentSectionProps) {
  return (
    <section>
      <ScholarshipList scholarships={scholarships} />
    </section>
  );
}