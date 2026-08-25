export interface Scholarship {
  id: string;
  title: string;
  university: string;
  degree: string;
  field: string;
  funding: string;
  deadline: string | null;
  status: string;

  requirements: string[];
  documentsRequired: string[];
  aiSummary: string;
  applicationLink: string;
  sourceUrl: string;
}