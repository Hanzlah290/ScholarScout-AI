"use client";

import { useEffect, useMemo, useState } from "react";

import ContentSection from "@/components/layout/ContentSection";
import Navbar from "@/components/layout/Navbar";
import SearchSection from "@/components/layout/SearchSection";
import StatsSection from "@/components/layout/StatsSection";
import { getScholarships } from "@/services/scholarshipService";
import type { Scholarship } from "@/types/scholarship";

export default function DashboardClient() {
  const [scholarships, setScholarships] = useState<Scholarship[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    async function fetchFreshData() {
      setLoading(true);
      const data = await getScholarships();
      setScholarships(data);
      setLoading(false);
    }

    fetchFreshData();
  }, []);

  const filteredScholarships = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();

    if (!query) {
      return scholarships;
    }

    return scholarships.filter((scholarship) => {
      return (
        scholarship.title.toLowerCase().includes(query) ||
        scholarship.university.toLowerCase().includes(query) ||
        scholarship.degree.toLowerCase().includes(query) ||
        scholarship.field.toLowerCase().includes(query)
      );
    });
  }, [scholarships, searchQuery]);

  return (
    <main className="min-h-screen bg-background">
      <div className="mx-auto flex max-w-6xl flex-col gap-4 p-4 sm:p-6">
        <Navbar />

        <SearchSection value={searchQuery} onChange={setSearchQuery} />

        <StatsSection />

        {loading ? (
          <div className="p-8 text-center text-muted-foreground">
            Loading scholarships from database...
          </div>
        ) : (
          <ContentSection scholarships={filteredScholarships} />
        )}
      </div>
    </main>
  );
}