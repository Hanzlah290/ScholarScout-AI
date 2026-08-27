"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import Navbar from "@/components/layout/Navbar";
import { getScholarshipById } from "@/services/scholarshipService";
import type { Scholarship } from "@/types/scholarship";

export default function ScholarshipDetailPage() {
  const params = useParams();
  const id = params?.id as string;

  const [scholarship, setScholarship] = useState<Scholarship | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      if (!id) return;
      setLoading(true);
      const data = await getScholarshipById(id);
      setScholarship(data);
      setLoading(false);
    }
    loadData();
  }, [id]);

  return (
    <main className="min-h-screen bg-background p-4 sm:p-6">
      <div className="mx-auto max-w-4xl space-y-6">
        <Navbar />

        <Link
          href="/"
          className="inline-flex items-center text-sm text-muted-foreground hover:underline"
        >
          ← Back to Dashboard
        </Link>

        {loading ? (
          <div className="p-8 text-center text-muted-foreground">
            Loading scholarship details...
          </div>
        ) : !scholarship ? (
          <div className="p-8 text-center text-muted-foreground">
            Scholarship not found.
          </div>
        ) : (
          <div className="rounded-lg border bg-card p-6 space-y-6 shadow-sm">
            <div>
              <h1 className="text-2xl font-bold">{scholarship.title}</h1>
              <p className="text-sm text-muted-foreground">{scholarship.university}</p>
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 text-sm border-y py-4">
              <p><strong>Degree Level:</strong> {scholarship.degree}</p>
              <p><strong>Field of Study:</strong> {scholarship.field}</p>
              <p><strong>Funding Type:</strong> {scholarship.funding}</p>
              <p><strong>Deadline:</strong> {scholarship.deadline || "Not specified"}</p>
            </div>

            <div>
              <h3 className="font-semibold text-base mb-2">🤖 AI Summary & Coverage</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {scholarship.aiSummary}
              </p>
            </div>

            {scholarship.requirements.length > 0 && (
              <div>
                <h3 className="font-semibold text-base mb-2">📋 Eligibility & Requirements</h3>
                <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
                  {scholarship.requirements.map((req, idx) => (
                    <li key={idx}>{req}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="pt-4 border-t flex justify-end">
              <a
                href={scholarship.applicationLink || scholarship.sourceUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition"
              >
                Apply on Official University Website ↗
              </a>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}