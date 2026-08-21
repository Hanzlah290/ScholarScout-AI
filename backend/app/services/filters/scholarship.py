from __future__ import annotations

import re

from bs4 import BeautifulSoup

from app.schemas.pipeline import DownloadedPage, FilteredPage


# Strong evidence that a page is about financial support.
STRONG_KEYWORDS = (
    "scholarship",
    "scholarships",
    "financial aid",
    "financial aids",
    "financial support",
    "tuition waiver",
    "fellowship",
    "funding",
    "grant",
    "stipend",
)


# Evidence that the opportunity includes the target degree level.
SUPPORTING_KEYWORDS = (
    "international student",
    "international students",
    "graduate admission",
    "postgraduate",
    "master",
    "master's",
    "masters",
)


# Target computing-related fields for V1.
TARGET_FIELD_KEYWORDS = (
    "software engineering",
    "computer science",
    "computer science and technology",
    "software technology",
    "information technology",
    "information systems",
    "computer engineering",
    "computing",
    "informatics",
    "cybersecurity",
    "cyber security",
    "cyber",
    "cyberspace",
    "artificial intelligence",
    "machine learning",
    "data science",
)


# Scholarship language strong enough to identify a scholarship page.
DEFINITIVE_SCHOLARSHIP_KEYWORDS = (
    "scholarship",
    "scholarships",
    "financial aid",
    "financial aids",
    "financial support",
    "tuition waiver",
    "fellowship",
)


# These words can indicate funding, but are too ambiguous by themselves.
AMBIGUOUS_SUPPORT_KEYWORDS = (
    "funding",
    "grant",
    "stipend",
)


# Concrete student-benefit / application evidence.
BENEFIT_KEYWORDS = (
    "tuition",
    "living allowance",
    "living expenses",
    "accommodation",
    "residence",
    "room and board",
    "food allowance",
    "insurance",
    "monthly allowance",
    "monthly stipend",
    "application deadline",
    "eligibility",
    "application requirements",
    "application procedure",
)


# Academic-program pages that commonly contain scholarship links
# or generic funding references but are not themselves opportunities.
ACADEMIC_ONLY_KEYWORDS = (
    "admission",
    "admissions",
    "major",
    "majors",
    "program",
    "programs",
    "curriculum",
    "course",
    "courses",
    "department",
    "departments",
    "faculty",
    "supervisor",
    "supervisors",
    "school of",
    "college of",
)


UNDERGRADUATE_KEYWORDS = (
    "bachelor",
    "bachelor's",
    "bsc",
    "undergraduate",
)


DOCTORAL_KEYWORDS = (
    "phd",
    "ph.d",
    "doctoral",
    "doctorate",
)


# Obvious non-content / institutional pages.
EXCLUDED_URL_TERMS = (
    "/ourstory",
    "/leadership",
    "/governance",
    "/schoolsandoffices",
    "/factsandfigures",
    "/about",
    "/campus",
    "/history",
    "/contact",
)


# Error pages must never become scholarship candidates.
ERROR_PAGE_KEYWORDS = (
    "404",
    "404 not found",
    "page not found",
    "page doesn't exist",
    "page does not exist",
    "access denied",
    "forbidden",
    "server error",
    "internal server error",
)


# Scholarship pages which describe historical/admin information rather
# than an actual opportunity.
ADMINISTRATIVE_PAGE_KEYWORDS = (
    "scholarship regulations",
    "regulations for scholarship",
    "scholarship issuance",
    "scholarship results",
    "results of the scholarship",
    "results of scholarship",
    "scholarship recipients",
    "scholarship recipient",
    "scholarship award results",
    "award results",
    "list of scholarship recipients",
    "selected scholarship recipients",
    "selected recipients",
    "recipient list",
)


# Evidence that a scholarship page is an active opportunity.
ACTIVE_OPPORTUNITY_KEYWORDS = (
    "apply",
    "application",
    "application deadline",
    "application procedure",
    "how to apply",
    "eligibility",
    "eligible",
    "application requirements",
    "call for applications",
)


# HTML elements which normally contain global/template content rather
# than page-specific scholarship content.
BOILERPLATE_TAGS = (
    "script",
    "style",
    "noscript",
    "svg",
    "nav",
    "header",
    "footer",
    "aside",
    "form",
)


MAIN_TAGS = (
    "main",
    "article",
)


def _normalize(text: str) -> str:
    """Normalize whitespace and casing."""
    return re.sub(r"\s+", " ", text).strip().lower()


def _contains(text: str, keyword: str) -> bool:
    """
    Match a phrase as a token rather than an arbitrary substring.

    Example:
        "master" matches "master's" only when explicitly represented
        in the keyword list; it does not match "masterful".
    """
    pattern = r"(?<!\w)" + re.escape(keyword) + r"(?!\w)"
    return re.search(
        pattern,
        text,
        flags=re.IGNORECASE,
    ) is not None


class ScholarshipPageFilter:
    """
    Cheap deterministic pre-filter for V1 scholarship candidates.

    The filter deliberately favors recall over final semantic certainty.
    It removes obvious template, academic, administrative, and error-page
    noise before Gemini while preserving plausible Master's scholarship
    opportunities and scholarship-index pages.
    """

    def __init__(
        self,
        strong_keywords: tuple[str, ...] = STRONG_KEYWORDS,
        supporting_keywords: tuple[str, ...] = SUPPORTING_KEYWORDS,
        target_field_keywords: tuple[str, ...] = TARGET_FIELD_KEYWORDS,
    ) -> None:
        self.strong_keywords = tuple(
            keyword.lower()
            for keyword in strong_keywords
        )

        self.supporting_keywords = tuple(
            keyword.lower()
            for keyword in supporting_keywords
        )

        self.target_field_keywords = tuple(
            keyword.lower()
            for keyword in target_field_keywords
        )

    # ------------------------------------------------------------------
    # BASIC PAGE CHECKS
    # ------------------------------------------------------------------

    def _is_error_page(
        self,
        title: str,
        content: str,
    ) -> bool:
        """Reject pages whose primary identity is an HTTP/site error page."""

        identity = _normalize(
            f"{title} {content[:500]}"
        )

        return any(
            _contains(identity, keyword)
            for keyword in ERROR_PAGE_KEYWORDS
        )

    def _is_administrative_scholarship_page(
        self,
        title: str,
        content: str,
    ) -> bool:
        """
        Only reject pages if they are purely historical awardee lists
        or result announcements, preserving active application notices.
        """
        identity = _normalize(f"{title} {content[:1500]}")

        # Check for explicit result/winner list markers
        result_keywords = (
            "awardee list", "recipient list", "admission results",
            "selection results", "获奖名单", "录取名单", "结果公示"
        )
        
        is_result_page = any(_contains(identity, kw) for kw in result_keywords)
        
        if not is_result_page:
            return False

        # If it's a result page, only keep it if active application criteria exist
        active_signal = any(
            _contains(identity, keyword)
            for keyword in ACTIVE_OPPORTUNITY_KEYWORDS
        )

        return not active_signal

    # ------------------------------------------------------------------
    # HTML CLEANING
    # ------------------------------------------------------------------

    def _clean_soup(
        self,
        html: str,
    ) -> BeautifulSoup:
        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        for element in soup.find_all(
            BOILERPLATE_TAGS
        ):
            element.decompose()

        for element in soup.find_all(
            attrs={
                "aria-hidden": lambda value:
                str(value).lower() == "true"
            }
        ):
            element.decompose()

        return soup

    # ------------------------------------------------------------------
    # CONTENT STRUCTURE
    # ------------------------------------------------------------------

    def _has_semantic_main(
        self,
        soup: BeautifulSoup,
    ) -> bool:
        """
        Determine whether the page contains a meaningful main/article
        content container.
        """

        if soup.find("main") or soup.find("article"):
            return True

        for tag in soup.find_all(
            ["div", "section"]
        ):
            attrs = " ".join(
                [
                    " ".join(tag.get("class", [])),
                    str(tag.get("id", "")),
                ]
            ).lower()

            if not any(
                token in attrs
                for token in (
                    "maincontent",
                    "main-content",
                    "page-content",
                    "article-content",
                    "entry-content",
                    "post-content",
                    "school-main",
                )
            ):
                continue

            text = tag.get_text(
                " ",
                strip=True,
            )

            if len(text) < 80:
                continue

            link_text = " ".join(
                link.get_text(
                    " ",
                    strip=True,
                )
                for link in tag.find_all("a")
            )

            if (
                len(link_text)
                / max(len(text), 1)
                <= 0.45
            ):
                return True

        return False

    def _extract_main_content(
        self,
        soup: BeautifulSoup,
    ) -> str:
        """
        Return the best available page-specific content.

        Preference order:
            1. main/article
            2. likely content containers
            3. cleaned body
        """

        for tag_name in MAIN_TAGS:
            candidates = soup.find_all(tag_name)

            if candidates:
                candidate = max(
                    candidates,
                    key=lambda tag:
                    len(
                        tag.get_text(
                            " ",
                            strip=True,
                        )
                    ),
                )

                return _normalize(
                    candidate.get_text(
                        " ",
                        strip=True,
                    )
                )

        candidates: list[tuple[int, str]] = []

        for tag in soup.find_all(
            ["div", "section"]
        ):
            attrs = " ".join(
                [
                    " ".join(tag.get("class", [])),
                    str(tag.get("id", "")),
                ]
            ).lower()

            if not any(
                token in attrs
                for token in (
                    "main",
                    "content",
                    "article",
                    "entry",
                    "post",
                    "body",
                )
            ):
                continue

            text = tag.get_text(
                " ",
                strip=True,
            )

            if len(text) >= 80:
                candidates.append(
                    (
                        len(text),
                        text,
                    )
                )

        if candidates:
            return _normalize(
                max(
                    candidates,
                    key=lambda item: item[0],
                )[1]
            )

        body = soup.body or soup

        return _normalize(
            body.get_text(
                " ",
                strip=True,
            )
        )

    # ------------------------------------------------------------------
    # MAIN FILTER
    # ------------------------------------------------------------------

    def filter(
        self,
        pages: list[DownloadedPage],
    ) -> list[FilteredPage]:
        results: list[FilteredPage] = []

        for page in pages:
            if self._is_error_page(
                page.title,
                page.html,
            ):
                continue

            matched = self._matches(page)

            if matched:
                results.append(
                    FilteredPage(
                        **page.model_dump(),
                        matched_keywords=matched,
                    )
                )

        return results

    # ------------------------------------------------------------------
    # PAGE MATCHING
    # ------------------------------------------------------------------

    def _matches(
        self,
        page: DownloadedPage,
    ) -> list[str]:
        url = str(page.url).lower()

        # --------------------------------------------------------------
        # 1. URL EXCLUSIONS
        # --------------------------------------------------------------

        if any(
            term in url
            for term in EXCLUDED_URL_TERMS
        ):
            return []

        # --------------------------------------------------------------
        # 2. CLEAN HTML
        # --------------------------------------------------------------

        soup = self._clean_soup(
            page.html
        )

        title = _normalize(
            soup.title.get_text(
                " ",
                strip=True,
            )
            if soup.title
            else page.title
        )

        h1 = _normalize(
            " ".join(
                heading.get_text(
                    " ",
                    strip=True,
                )
                for heading in soup.find_all("h1")
            )
        )

        headings = _normalize(
            " ".join(
                heading.get_text(
                    " ",
                    strip=True,
                )
                for heading in soup.find_all(
                    ["h1", "h2", "h3"]
                )
            )
        )

        has_semantic_main = (
            self._has_semantic_main(soup)
        )

        content = self._extract_main_content(
            soup
        )

        # --------------------------------------------------------------
        # 3. PAGE IDENTITY REJECTION
        # --------------------------------------------------------------
        #
        # These checks happen BEFORE scholarship matching.
        # Therefore:
        #
        # "Results of the 2026 Scholarship"
        #
        # cannot survive simply because "scholarship" is present.
        # --------------------------------------------------------------

        if self._is_error_page(
            title,
            content,
        ):
            return []

        if self._is_administrative_scholarship_page(
            title,
            content,
        ):
            return []

        # --------------------------------------------------------------
        # 4. KEYWORD EXTRACTION
        # --------------------------------------------------------------

        # Structural evidence intentionally uses URL + document title.
        # H2/H3 frequently contain navigation or directory labels.
        structural_text = _normalize(
            f"{url} {title}"
        )

        structural_strong = [
            keyword
            for keyword in self.strong_keywords
            if _contains(
                structural_text,
                keyword,
            )
        ]

        content_strong = [
            keyword
            for keyword in self.strong_keywords
            if _contains(
                content,
                keyword,
            )
        ]

        content_definitive = [
            keyword
            for keyword in DEFINITIVE_SCHOLARSHIP_KEYWORDS
            if _contains(
                content,
                keyword,
            )
        ]

        structural_definitive = [
            keyword
            for keyword in DEFINITIVE_SCHOLARSHIP_KEYWORDS
            if _contains(
                structural_text,
                keyword,
            )
        ]

        content_ambiguous = [
            keyword
            for keyword in AMBIGUOUS_SUPPORT_KEYWORDS
            if _contains(
                content,
                keyword,
            )
        ]

        content_supporting = [
            keyword
            for keyword in self.supporting_keywords
            if _contains(
                content,
                keyword,
            )
        ]

        content_fields = [
            keyword
            for keyword in self.target_field_keywords
            if _contains(
                content,
                keyword,
            )
        ]

        content_benefits = [
            keyword
            for keyword in BENEFIT_KEYWORDS
            if _contains(
                content,
                keyword,
            )
        ]

        # Preserve useful evidence for FilteredPage.
        matched = list(
            dict.fromkeys(
                structural_strong
                + content_strong
                + content_supporting
                + content_fields
                + content_benefits
            )
        )

        if not matched:
            return []

        # --------------------------------------------------------------
        # 5. DEGREE ANALYSIS
        # --------------------------------------------------------------

        degree_text = _normalize(
            f"{title} {h1} {content}"
        )

        has_masters_anywhere = any(
            _contains(
                degree_text,
                keyword,
            )
            for keyword in self.supporting_keywords
        )

        has_undergraduate = any(
            _contains(
                degree_text,
                keyword,
            )
            for keyword in UNDERGRADUATE_KEYWORDS
        )

        has_doctoral = any(
            _contains(
                degree_text,
                keyword,
            )
            for keyword in DOCTORAL_KEYWORDS
        )

        # V1 targets Master's opportunities.
        #
        # If the page explicitly talks only about undergraduate/doctoral
        # study and contains no Master's evidence, reject it.
        #
        # Mixed-degree pages remain eligible.
        if (
            not has_masters_anywhere
            and (
                has_undergraduate
                or has_doctoral
            )
        ):
            return []

        # --------------------------------------------------------------
        # 6. ACADEMIC-PROGRAM NOISE
        # --------------------------------------------------------------

        page_identity = _normalize(
            f"{title} {h1} {content[:900]}"
        )

        has_target_field = bool(
            content_fields
        )

        has_benefit = bool(
            content_benefits
        )

        academic_page = any(
            _contains(
                page_identity,
                keyword,
            )
            for keyword in ACADEMIC_ONLY_KEYWORDS
        )

        # A specific academic program should not become a scholarship
        # candidate merely because the university template contains
        # scholarship/funding links.
        if (
            academic_page
            and not has_target_field
            and not structural_definitive
        ):
            return []

        # --------------------------------------------------------------
        # 7. EXPLICIT SCHOLARSHIP PAGE
        # --------------------------------------------------------------

        # URL/title explicitly identifies the page as scholarship-related.
        #
        # Example:
        #     /scholarships
        #     "International Scholarships"
        #
        # This is strong enough to survive sparse JavaScript-rendered
        # bodies.
        if structural_definitive:
            return matched

        # --------------------------------------------------------------
        # 8. BODY MUST CONTAIN REAL SCHOLARSHIP EVIDENCE
        # --------------------------------------------------------------

        if not content_definitive:
            return []

        definitive_occurrences = sum(
            len(
                re.findall(
                    r"(?<!\w)"
                    + re.escape(keyword)
                    + r"(?!\w)",
                    content,
                    flags=re.IGNORECASE,
                )
            )
            for keyword in DEFINITIVE_SCHOLARSHIP_KEYWORDS
        )

        # If no semantic main/article/content container exists,
        # the fallback body can still contain global template/navigation
        # content. Require repeated scholarship evidence.
        if (
            not has_semantic_main
            and definitive_occurrences < 2
        ):
            return []

        # --------------------------------------------------------------
        # 9. MASTER'S PAGE
        # --------------------------------------------------------------

        if has_masters_anywhere:
            return matched

        # --------------------------------------------------------------
        # 10. TARGET COMPUTING FIELD
        # --------------------------------------------------------------

        if has_target_field:
            return matched

        # --------------------------------------------------------------
        # 11. CONCRETE BENEFITS
        # --------------------------------------------------------------

        if has_benefit:
            return matched

        # --------------------------------------------------------------
        # 12. MULTIPLE DEFINITIVE SCHOLARSHIP SIGNALS
        # --------------------------------------------------------------

        if len(
            set(content_definitive)
        ) >= 2:
            return matched

        # --------------------------------------------------------------
        # 13. OTHERWISE REJECT
        # --------------------------------------------------------------

        return []