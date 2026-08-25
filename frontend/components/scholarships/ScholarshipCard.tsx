import Link from "next/link";

import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import type { Scholarship } from "@/types/scholarship";

interface ScholarshipCardProps {
  scholarship: Scholarship;
}

export default function ScholarshipCard({
  scholarship,
}: ScholarshipCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">{scholarship.title}</CardTitle>

        <p className="text-sm text-muted-foreground">
          {scholarship.university}
        </p>
      </CardHeader>

      <CardContent className="space-y-2 text-sm">
        <div>
          <span className="font-medium">Degree:</span>{" "}
          {scholarship.degree}
        </div>

        <div>
          <span className="font-medium">Field:</span>{" "}
          {scholarship.field}
        </div>

        <div>
          <span className="font-medium">Funding:</span>{" "}
          {scholarship.funding}
        </div>

        <div>
          <span className="font-medium">Deadline:</span>{" "}
          {scholarship.deadline ?? "Not specified"}
        </div>
      </CardContent>

      <CardFooter className="flex items-center justify-between">
        <span className="text-sm text-muted-foreground">
          {scholarship.status}
        </span>

        <Link
          href={`/scholarships/${scholarship.id}`}
          className="text-sm font-medium underline-offset-4 hover:underline"
        >
          View Details
        </Link>
      </CardFooter>
    </Card>
  );
}
