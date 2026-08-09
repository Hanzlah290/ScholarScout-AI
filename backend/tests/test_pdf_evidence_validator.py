from app.schemas.pipeline import PDFScholarshipEvidence
from app.services.pdf.evidence_validator import (
    PDFEvidenceValidator,
)


def main() -> None:
    print("=== PDF EVIDENCE VALIDATOR TEST ===")

    validator = PDFEvidenceValidator()

    # 1. CSC must be rejected.
    csc = PDFScholarshipEvidence(
        is_scholarship=True,
        scholarship_name=(
            "Chinese Government Scholarship "
            "(CSC) University Program (Type B)"
        ),
        scholarship_evidence=(
            "A. Chinese Government Scholarship (CSC)"
        ),
        funding_evidence="Full scholarship",
        deadline_evidence="April 15, 2026",
        degree_evidence="Master's programs",
        field_evidence="Computer Science and Technology",
        application_evidence=(
            "http://apply.isc.bit.edu.cn/"
        ),
    )

    accepted, reason = validator.validate(csc)

    print()
    print("CSC test:")
    print("Accepted:", accepted)
    print("Reason:", reason)

    assert accepted is False
    assert "CSC" in reason

    # 2. A valid in-scope scholarship should pass.
    valid = PDFScholarshipEvidence(
        is_scholarship=True,
        scholarship_name="BIT International Student Scholarship",
        scholarship_evidence=(
            "BIT International Student Scholarship"
        ),
        funding_evidence="Tuition scholarship",
        deadline_evidence="May 1, 2026",
        degree_evidence="Master's degree",
        field_evidence=(
            "Computer Science and Technology"
        ),
        application_evidence=(
            "http://apply.isc.bit.edu.cn/"
        ),
    )

    accepted, reason = validator.validate(valid)

    print()
    print("Valid scholarship test:")
    print("Accepted:", accepted)
    print("Reason:", reason)

    assert accepted is True
    assert reason == ""

    # 3. Non-computing field should be rejected.
    wrong_field = PDFScholarshipEvidence(
        is_scholarship=True,
        scholarship_name="Example Scholarship",
        scholarship_evidence="Example Scholarship",
        funding_evidence="Tuition support",
        deadline_evidence="May 1, 2026",
        degree_evidence="Master's degree",
        field_evidence="Mechanical Engineering",
        application_evidence=(
            "http://apply.isc.bit.edu.cn/"
        ),
    )

    accepted, reason = validator.validate(wrong_field)

    print()
    print("Wrong field test:")
    print("Accepted:", accepted)
    print("Reason:", reason)

    assert accepted is False
    assert "computing" in reason.lower()

    print()
    print("=== ALL PDF EVIDENCE VALIDATOR TESTS PASSED ===")


if __name__ == "__main__":
    main()
