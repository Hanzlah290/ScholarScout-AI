import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { Scholarship } from "@/types/scholarship";

interface StatsSectionProps {
  scholarships?: Scholarship[];
  sourcesCount?: number;
  lastScanAt?: string | null;
}

export default function StatsSection({
  scholarships = [],
  sourcesCount = 0,
  lastScanAt,
}: StatsSectionProps) {
  // Compute live metrics directly from PostgreSQL data
  const openScholarships = scholarships.filter((s) => s.status === "Active").length;
  const uniqueUniversities = new Set(scholarships.map((s) => s.university)).size;
  
  // Format Last Scan timestamp safely
  const formattedLastScan = lastScanAt
    ? new Date(lastScanAt).toLocaleString()
    : scholarships.length > 0
    ? "Active"
    : "--";

  return (
    <section className="grid grid-cols-1 gap-4 sm:grid-cols-4">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            Open Scholarships
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-2xl font-semibold">{openScholarships}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            Universities
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-2xl font-semibold">{uniqueUniversities}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            Total Sources
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-2xl font-semibold">{sourcesCount || uniqueUniversities}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            Last Scan
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-2xl font-semibold">{formattedLastScan}</p>
        </CardContent>
      </Card>
    </section>
  );
}