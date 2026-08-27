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

export default function ScholarshipCard({ scholarship }: ScholarshipCardProps) {
  return (
    <Card className="flex flex-col justify-between">
      <CardHeader>
        <CardTitle className="text-base font-semibold leading-tight">
          {scholarship.title}
        </CardTitle>
        <p className="text-xs text-muted-foreground">{scholarship.university}</p>
      </CardHeader>

      <CardContent className="space-y-2 text-xs">
        <p><strong>Degree:</strong> {scholarship.degree}</p>
        <p><strong>Field:</strong> {scholarship.field}</p>
        <p><strong>Funding:</strong> {scholarship.funding}</p>
        <p><strong>Deadline:</strong> {scholarship.deadline || "N/A"}</p>
      </CardContent>

      <CardFooter className="flex items-center justify-between border-t pt-3">
        <span className="text-xs text-muted-foreground">{scholarship.status}</span>
        
        <div className="flex gap-2">
          {/* Internal detail page */}
          <Link
            href={`/scholarships/${scholarship.id}`}
            className="text-xs font-medium text-muted-foreground hover:underline"
          >
            Details
          </Link>

          {/* External direct university link */}
          <a
            href={scholarship.applicationLink || scholarship.sourceUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded bg-primary px-2.5 py-1 text-xs font-medium text-primary-foreground hover:bg-primary/90"
          >
            Apply Now ↗
          </a>
        </div>
      </CardFooter>
    </Card>
  );
}