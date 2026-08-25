import Link from "next/link";
import { notFound } from "next/navigation";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { getScholarshipById } from "@/services/scholarshipService";

interface ScholarshipDetailsPageProps {
  params: Promise<{
    id: string;
  }>;
}

export default async function ScholarshipDetailsPage({
  params,
}: ScholarshipDetailsPageProps) {
  const { id } = await params;

  const scholarship = await getScholarshipById(id);

  if (!scholarship) {
    notFound();
  }

  return (
    <main className="min-h-screen bg-background">
      <div className="mx-auto max-w-4xl space-y-4 p-4 sm:p-6">
        <Link
          href="/"
          className="text-sm text-muted-foreground hover:underline"
        >
          ← Back to Dashboard
        </Link>

        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">
              {scholarship.title}
            </CardTitle>

            <p className="text-muted-foreground">
              {scholarship.university}
            </p>
          </CardHeader>

          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <p className="text-sm text-muted-foreground">
                  Degree
                </p>
                <p>{scholarship.degree}</p>
              </div>

              <div>
                <p className="text-sm text-muted-foreground">
                  Field
                </p>
                <p>{scholarship.field}</p>
              </div>

              <div>
                <p className="text-sm text-muted-foreground">
                  Funding
                </p>
                <p>{scholarship.funding}</p>
              </div>

              <div>
                <p className="text-sm text-muted-foreground">
                  Deadline
                </p>
                <p>{scholarship.deadline ?? "Not specified"}</p>
              </div>

              <div>
                <p className="text-sm text-muted-foreground">
                  Status
                </p>
                <p>{scholarship.status}</p>
              </div>
            </div>

            <section>
              <h2 className="mb-2 text-lg font-semibold">
                AI Summary
              </h2>

              <p className="text-sm leading-6 text-muted-foreground">
                {scholarship.aiSummary}
              </p>
            </section>

            <section>
              <h2 className="mb-2 text-lg font-semibold">
                Requirements
              </h2>

              <ul className="list-disc space-y-1 pl-5 text-sm">
                {scholarship.requirements.map((requirement) => (
                  <li key={requirement}>{requirement}</li>
                ))}
              </ul>
            </section>

            <section>
              <h2 className="mb-2 text-lg font-semibold">
                Required Documents
              </h2>

              <ul className="list-disc space-y-1 pl-5 text-sm">
                {scholarship.documentsRequired.map((document) => (
                  <li key={document}>{document}</li>
                ))}
              </ul>
            </section>

            <div className="flex flex-col gap-3 sm:flex-row">
              <a
                href={scholarship.applicationLink}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-md bg-primary px-4 py-2 text-center text-sm font-medium text-primary-foreground"
              >
                Apply
              </a>

              <a
                href={scholarship.sourceUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-md border px-4 py-2 text-center text-sm font-medium"
              >
                Original Source
              </a>
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
