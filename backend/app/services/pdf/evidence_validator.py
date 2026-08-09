from __future__ import annotations

from app.schemas.pipeline import PDFScholarshipEvidence


class PDFEvidenceValidator:
    """
    Validate PDF scholarship evidence against ScholarScout AI
    Version 1 scope.

    This validator does not extract or invent information.
    It only decides whether already-extracted evidence is
    sufficient and within scope.
    """

    EXCLUDED_SCHOLARSHIPS = (
        "chinese government scholarship",
        "csc",
    )

    ALLOWED_COUNTRY = "china"

    TARGET_DEGREE_TERMS = (
        "master",
        "master's",
        "masters",
        "硕士",
    )

    TARGET_FIELD_TERMS = (
        "software engineering",
        "computer science",
        "computer science and technology",
        "software",
        "computing",
        "computer engineering",
        "information technology",
        "information science",
        "computer technology",
    )

    def validate(
        self,
        evidence: PDFScholarshipEvidence,
    ) -> tuple[bool, str]:
        """
        Return:

            (True, "") when the evidence passes.

            (False, reason) when it must be rejected.
        """

        if not evidence.is_scholarship:
            return False, "PDF is not identified as a scholarship."

        scholarship_name = (
            evidence.scholarship_name.strip().lower()
        )

        scholarship_evidence = (
            evidence.scholarship_evidence.strip().lower()
        )

        combined_name_evidence = (
            f"{scholarship_name} "
            f"{scholarship_evidence}"
        )

        for excluded in self.EXCLUDED_SCHOLARSHIPS:
            if excluded in combined_name_evidence:
                return (
                    False,
                    "Excluded scholarship: "
                    "Chinese Government Scholarship (CSC).",
                )

        if not evidence.degree_evidence.strip():
            return (
                False,
                "Missing degree evidence.",
            )

        degree_text = evidence.degree_evidence.lower()

        if not any(
            term in degree_text
            for term in self.TARGET_DEGREE_TERMS
        ):
            return (
                False,
                "No Master's degree evidence.",
            )

        if not evidence.field_evidence.strip():
            return (
                False,
                "Missing field evidence.",
            )

        field_text = evidence.field_evidence.lower()

        if not any(
            term in field_text
            for term in self.TARGET_FIELD_TERMS
        ):
            return (
                False,
                "Field is outside the Version 1 computing target.",
            )

        if not evidence.application_evidence.strip():
            return (
                False,
                "Missing official application evidence.",
            )

        if not scholarship_name:
            return (
                False,
                "Missing scholarship name evidence.",
            )

        return True, ""