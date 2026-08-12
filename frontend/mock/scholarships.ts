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
  },
];