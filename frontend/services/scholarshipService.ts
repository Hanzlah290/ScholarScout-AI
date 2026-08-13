import { mockScholarships } from "@/mock/scholarships";
import type { Scholarship } from "@/types/scholarship";

export async function getScholarships(): Promise<Scholarship[]> {
  return mockScholarships;
}

export async function getScholarshipById(
  id: string
): Promise<Scholarship | null> {
  return mockScholarships.find((scholarship) => scholarship.id === id) ?? null;
}
