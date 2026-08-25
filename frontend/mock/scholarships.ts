import type { Scholarship } from "@/types/scholarship";

export const mockScholarships: Scholarship[] = [
  {
    id: "1",
    title: "International Graduate Scholarship",
    university: "Tsinghua University",
    degree: "Master's",
    field: "Software Engineering",
    funding: "Fully Funded",
    deadline: "2027-03-31",
    status: "Open",

    requirements: [
      "Bachelor's degree",
      "Strong academic record",
      "English language proficiency",
    ],

    documentsRequired: [
      "Passport",
      "Bachelor's transcript",
      "Bachelor's degree certificate",
      "Recommendation letters",
      "Personal statement",
    ],

    aiSummary:
      "A fully funded scholarship for international graduate students interested in Master's-level study.",

    applicationLink: "https://example.com/apply",

    sourceUrl: "https://example.com/scholarship",
  },

  {
    id: "2",
    title: "International Student Scholarship",
    university: "Zhejiang University",
    degree: "Master's",
    field: "Computer Science",
    funding: "Partial",
    deadline: "2027-04-15",
    status: "Open",

    requirements: [
      "Bachelor's degree",
      "Academic transcripts",
    ],

    documentsRequired: [
      "Passport",
      "Transcript",
      "Personal statement",
    ],

    aiSummary:
      "A partial scholarship available for international Master's applicants.",

    applicationLink: "https://example.com/apply-2",

    sourceUrl: "https://example.com/scholarship-2",
  },

  {
    id: "3",
    title: "Graduate Excellence Scholarship",
    university: "Peking University",
    degree: "Master's",
    field: "Software Engineering",
    funding: "Fully Funded",
    deadline: "2027-02-28",
    status: "Open",

    requirements: [
      "Bachelor's degree",
      "Strong academic performance",
    ],

    documentsRequired: [
      "Passport",
      "Transcript",
      "Recommendation letters",
    ],

    aiSummary:
      "A graduate scholarship intended for high-performing international students.",

    applicationLink: "https://example.com/apply-3",

    sourceUrl: "https://example.com/scholarship-3",
  },
];