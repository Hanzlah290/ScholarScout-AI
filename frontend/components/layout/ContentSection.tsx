import ScholarshipCard from "@/components/scholarships/ScholarshipCard";
import { mockScholarship } from "@/mock/scholarships";

export default function ContentSection() {
  return (
    <section>
      <ScholarshipCard scholarship={mockScholarship} />
    </section>
  );
}