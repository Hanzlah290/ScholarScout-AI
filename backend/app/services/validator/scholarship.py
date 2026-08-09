from future import annotations

import re

from bs4 import BeautifulSoup

from app.schemas.pipeline import DownloadedPage, FilteredPage

STRONG_KEYWORDS = (
"scholarship",
"scholarships",
"financial aid",
"financial support",
"tuition waiver",
"fellowship",
"funding",
"grant",
"stipend",
)

SUPPORTING_KEYWORDS = (
"international student",
"international students",
"graduate admission",
"admission",
"master",
"masters",
"postgraduate",
)

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

class ScholarshipPageFilter:



def __init__(
    self,
    strong_keywords: tuple[str, ...] = STRONG_KEYWORDS,
    supporting_keywords: tuple[str, ...] = SUPPORTING_KEYWORDS,
) -> None:
    self.strong_keywords = tuple(
        keyword.lower()
        for keyword in strong_keywords
    )
    self.supporting_keywords = tuple(
        keyword.lower()
        for keyword in supporting_keywords
    )

def filter(
    self,
    pages: list[DownloadedPage],
) -> list[FilteredPage]:
    results: list[FilteredPage] = []

    for page in pages:
        matched = self._matches(page)

        if matched:
            results.append(
                FilteredPage(
                    **page.model_dump(),
                    matched_keywords=matched,
                )
            )

    return results

def _matches(
    self,
    page: DownloadedPage,
) -> list[str]:
    url = str(page.url).lower()

    if any(term in url for term in EXCLUDED_URL_TERMS):
        return []

    soup = BeautifulSoup(page.html, "html.parser")

    for element in soup(
        ["script", "style", "noscript", "svg"]
    ):
        element.decompose()

    title = (
        soup.title.get_text(" ", strip=True)
        if soup.title
        else page.title
    )

    headings = " ".join(
        heading.get_text(" ", strip=True)
        for heading in soup.find_all(["h1", "h2", "h3"])
    )

    body = soup.get_text(" ", strip=True)

    title = re.sub(r"\s+", " ", title).lower()
    headings = re.sub(r"\s+", " ", headings).lower()
    body = re.sub(r"\s+", " ", body).lower()

    structural_text = f"{url} {title} {headings}"

    strong_structural = [
        keyword
        for keyword in self.strong_keywords
        if keyword in structural_text
    ]

    strong_body = [
        keyword
        for keyword in self.strong_keywords
        if keyword in body
    ]

    supporting_body = [
        keyword
        for keyword in self.supporting_keywords
        if keyword in body
    ]

    matched = list(
        dict.fromkeys(
            strong_structural
            + strong_body
            + supporting_body
        )
    )

    # Best case:
    # A scholarship/funding term appears in the URL, title,
    # or heading. This is strong page-level evidence.
    if strong_structural:
        return matched

    # If there is no structural evidence, require at least
    # two different strong scholarship signals in the body.
    if len(set(strong_body)) >= 2:
        return matched

    # A single strong term in the body is only accepted when
    # there is also supporting evidence that the page concerns
    # graduate/international admissions.
    if strong_body and supporting_body:
        return matched

    return []
