"use client";

import { useMemo, useState } from "react";

import Navbar from "@/components/layout/Navbar";
import SearchSection from "@/components/layout/SearchSection";
import StatsSection from "@/components/layout/StatsSection";
import ContentSection from "@/components/layout/ContentSection";
import { mockScholarships } from "@/mock/scholarships";

export default function Home() {
  const [searchQuery, setSearchQuery] = useState("");

  const filteredScholarships = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();

    if (!query) {
      return mockScholarships;
    }

    return mockScholarships.filter((scholarship) => {
      return (
        scholarship.title.toLowerCase().includes(query) ||
        scholarship.university.toLowerCase().includes(query) ||
        scholarship.degree.toLowerCase().includes(query) ||
        scholarship.field.toLowerCase().includes(query)
      );
    });
  }, [searchQuery]);

  return (
    <main className="min-h-screen bg-background">
      <div className="mx-auto flex max-w-6xl flex-col gap-4 p-4 sm:p-6">
        <Navbar />

        <SearchSection
          value={searchQuery}
          onChange={setSearchQuery}
        />

        <StatsSection />

        <ContentSection scholarships={filteredScholarships} />
      </div>
    </main>
  );
}