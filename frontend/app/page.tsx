import DashboardClient from "@/components/scholarships/DashboardClient";
import { getScholarships } from "@/services/scholarshipService";

export default async function Home() {
  const scholarships = await getScholarships();

  return <DashboardClient scholarships={scholarships} />;
}