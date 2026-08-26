import type { Scholarship } from "@/types/scholarship";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

/**
 * Maps raw backend database JSON to match your frontend TypeScript Scholarship interface cleanly.
 */
function mapBackendScholarship(data: any): Scholarship {
  return {
    id: String(data.id),
    title: data.title || "Untitled Scholarship",
    university: data.university || "University",
    degree: data.degree || "Master's / PhD",
    field: data.field || "General",
    funding: data.funding || "Full / Partial Coverage",
    deadline: data.deadline ? String(data.deadline) : null,
    // Safely default status to Active if is_active is true or undefined
    status: data.is_active === false ? "Closed" : "Active",

    requirements: Array.isArray(data.eligibility_rules)
      ? data.eligibility_rules
      : typeof data.eligibility_rules === "string"
      ? [data.eligibility_rules]
      : [],
    documentsRequired: Array.isArray(data.documents_required)
      ? data.documents_required
      : typeof data.documents_required === "string"
      ? [data.documents_required]
      : [],
    aiSummary:
      data.ai_summary ||
      data.funding ||
      "No detailed AI summary available.",
    applicationLink: data.application_link || data.source_url || "#",
    sourceUrl: data.source_url || "#",
  };
}

export async function getScholarships(): Promise<Scholarship[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/scholarships`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });

    if (!response.ok) {
      throw new Error(`Error fetching scholarships: ${response.statusText}`);
    }

    const data = await response.json();

    // Check all common list response wrappers
    let rawList: any[] = [];
    if (Array.isArray(data)) {
      rawList = data;
    } else if (data && Array.isArray(data.items)) {
      rawList = data.items;
    } else if (data && Array.isArray(data.scholarships)) {
      rawList = data.scholarships;
    } else if (data && Array.isArray(data.data)) {
      rawList = data.data;
    }

    return rawList.map(mapBackendScholarship);
  } catch (error) {
    console.error("Failed to fetch scholarships from backend:", error);
    return [];
  }
}



export async function getScholarshipById(
  id: string
): Promise<Scholarship | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/scholarships/${id}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });

    if (response.status === 404) {
      return null;
    }

    if (!response.ok) {
      throw new Error(`Error fetching scholarship ${id}: ${response.statusText}`);
    }

    const data = await response.json();
    return mapBackendScholarship(data);
  } catch (error) {
    console.error(`Failed to fetch scholarship ${id} from backend:`, error);
    return null;
  }
}