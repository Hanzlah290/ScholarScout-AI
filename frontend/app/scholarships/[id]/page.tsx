"use client";

import { useEffect, useState } from "react";
import { getScholarships } from "@/services/scholarshipService";
import type { Scholarship } from "@/types/scholarship";

export default function Home() {
  const [scholarships, setScholarships] = useState<Scholarship[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState<string>("");

  useEffect(() => {
    async function fetchFreshData() {
      setLoading(true);
      const data = await getScholarships();
      setScholarships(data);
      setLoading(false);
    }
    fetchFreshData();
  }, []);

  // Compute stats dynamically from backend response
  const openScholarshipsCount = scholarships.filter(
    (s) => s.status === "Active"
  ).length;

  const filteredScholarships = scholarships.filter(
    (s) =>
      s.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.university.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <main className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center border p-4 rounded-lg bg-white shadow-sm">
        <div>
          <h1 className="text-xl font-bold flex items-center gap-2">
            🎓 ScholarScout AI
          </h1>
          <p className="text-sm text-gray-500">China Scholarship Dashboard</p>
        </div>
        <span className="text-xs text-gray-400">
          Last Scan: {scholarships.length > 0 ? "Just now" : "--"}
        </span>
      </div>

      {/* Search Input */}
      <input
        type="text"
        placeholder="Search scholarships..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
      />

      {/* Dynamic Stats Cards */}
      <div className="grid grid-cols-3 gap-4">
        <div className="border p-5 rounded-lg bg-white shadow-sm">
          <p className="text-sm font-medium text-gray-600">Open Scholarships</p>
          <p className="text-3xl font-bold mt-2">{openScholarshipsCount}</p>
        </div>
        <div className="border p-5 rounded-lg bg-white shadow-sm">
          <p className="text-sm font-medium text-gray-600">Total Extracted</p>
          <p className="text-3xl font-bold mt-2">{scholarships.length}</p>
        </div>
        <div className="border p-5 rounded-lg bg-white shadow-sm">
          <p className="text-sm font-medium text-gray-600">Active Sources</p>
          <p className="text-3xl font-bold mt-2">
            {new Set(scholarships.map((s) => s.university)).size}
          </p>
        </div>
      </div>

      {/* Scholarship List or Empty State */}
      <div className="border rounded-lg p-8 bg-white text-center shadow-sm">
        {loading ? (
          <p className="text-gray-500">Loading scholarships from database...</p>
        ) : filteredScholarships.length > 0 ? (
          <div className="grid gap-4 text-left">
            {filteredScholarships.map((item) => (
              <div
                key={item.id}
                className="border p-4 rounded-md hover:shadow-md transition"
              >
                <h3 className="font-bold text-lg text-blue-600">{item.title}</h3>
                <p className="text-sm text-gray-600">
                  {item.university} • {item.degree}
                </p>
                <p className="text-xs text-gray-400 mt-2">
                  Deadline: {item.deadline || "N/A"}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 font-medium">No scholarships found.</p>
        )}
      </div>
    </main>
  );
}