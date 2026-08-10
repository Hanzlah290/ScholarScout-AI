from __future__ import annotations

from datetime import date

from app.models.source import Source
from app.schemas.pipeline import (
    ScholarshipExtraction,
    StoredPage,
    ValidatedScholarship,
)


class ScholarshipValidator:
    """Validate extracted scholarships against Version 1 rules."""

    ALLOWED_COUNTRY = "China"

    TARGET_DEGREE_KEYWORDS = (
        "master",
        "master's",
        "masters",
    )

    TARGET_FIELD_KEYWORDS = (
        "software engineering",
        "computer science",
        "computer science and technology",
        "software technology",
        "information technology",
        "information systems",
        "computing",
        "computer engineering",
        "informatics",
    )

    EXCLUDED_SCHOLARSHIP_KEYWORDS = (
        "chinese government scholarship",
        "csc scholarship",
        "csc",
    )

    def validate(
        self,
        extraction: ScholarshipExtraction,
        page: StoredPage,
        source: Source,
    ) -> ValidatedScholarship:
        """
        Validate one extracted scholarship against Version 1 rules.

        Version 1 scope:
        - Country must be China.
        - Scholarship must be a real scholarship.
        - CSC / Chinese Government Scholarship is excluded.
        - Target degree is Master's.
        - Target field is Software Engineering or a closely related
          computing field.
        - Application link must be HTTPS.
        """

        # ---------------------------------------------------------
        # 1. Scholarship must actually be identified
        # ---------------------------------------------------------
        if not extraction.is_scholarship:
            raise ValueError(
                "Source does not identify a valid scholarship opportunity."
            )

        # ---------------------------------------------------------
        # 2. Country scope
        # ---------------------------------------------------------
        if extraction.country.strip().lower() != self.ALLOWED_COUNTRY.lower():
            raise ValueError(
                "Scholarship country scope is limited to China."
            )

        # ---------------------------------------------------------
        # 3. CSC is explicitly outside Version 1 scope
        # ---------------------------------------------------------
        scholarship_text = (
            f"{extraction.title} "
            f"{extraction.summary}"
        ).lower()

        if any(
            keyword in scholarship_text
            for keyword in self.EXCLUDED_SCHOLARSHIP_KEYWORDS
        ):
            raise ValueError(
                "Chinese Government Scholarship (CSC) is outside "
                "Version 1 scope."
            )

        # ---------------------------------------------------------
        # 4. Target degree must be Master's
        # ---------------------------------------------------------
        degree_text = extraction.degree.lower()

        if not any(
            keyword in degree_text
            for keyword in self.TARGET_DEGREE_KEYWORDS
        ):
            raise ValueError(
                "Scholarship is outside the Version 1 Master's degree target."
            )

        # ---------------------------------------------------------
        # 5. Target field must be computing-related
        # ---------------------------------------------------------
        field_text = extraction.field.lower()

        if not any(
            keyword in field_text
            for keyword in self.TARGET_FIELD_KEYWORDS
        ):
            raise ValueError(
                "Field is outside the Version 1 computing target."
            )

        # ---------------------------------------------------------
        # 6. Application link must use HTTPS
        # ---------------------------------------------------------
        application_link = str(extraction.application_link)

        if not application_link.lower().startswith("https://"):
            raise ValueError(
                "Application link must use HTTPS."
            )

        # ---------------------------------------------------------
        # 7. Determine scholarship status
        # ---------------------------------------------------------
        status = "Open"

        if extraction.deadline is not None:
            if extraction.deadline < date.today():
                status = "Closed"

        # ---------------------------------------------------------
        # 8. Build validated scholarship
        # ---------------------------------------------------------
        return ValidatedScholarship(
            **extraction.model_dump(),
            source_id=source.id,
            source_url=page.url,
            raw_page_path=page.path,
            status=status,
        )