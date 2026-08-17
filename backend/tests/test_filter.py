from uuid import UUID

from app.schemas.pipeline import DownloadedPage
from app.services.filters.scholarship import ScholarshipPageFilter


SOURCE_ID = UUID("00000000-0000-0000-0000-000000000001")
FILTER = ScholarshipPageFilter()


def page(title: str, body: str, *, url: str = "https://example.edu.cn/page") -> DownloadedPage:
    return DownloadedPage(
        source_id=SOURCE_ID,
        url=url,
        title=title,
        html=f"""
        <html>
          <head><title>{title}</title></head>
          <body>
            <nav>
              Scholarship | International Students | Master | Computer Science
            </nav>
            <main>{body}</main>
            <footer>Scholarship | Postgraduate | Computer Science</footer>
          </body>
        </html>
        """,
    )


def kept(title: str, body: str, *, url: str = "https://example.edu.cn/page") -> bool:
    return bool(FILTER.filter([page(title, body, url=url)]))


def test_masters_software_engineering_scholarship_is_kept():
    assert kept(
        "Master Scholarship in Software Engineering",
        """
        Tuition waiver. Accommodation provided. Monthly living allowance.
        Application deadline: 30 June.
        """,
    )


def test_masters_computer_science_scholarship_is_kept():
    assert kept(
        "International Scholarship",
        """
        Master's students in Computer Science are eligible.
        Tuition is fully covered and accommodation is provided.
        """,
    )


def test_university_wide_masters_scholarship_without_field_is_kept():
    assert kept(
        "International Student Scholarship",
        """
        The scholarship is available to Master's students.
        It covers tuition, accommodation, insurance and living expenses.
        """,
    )


def test_scholarship_index_page_is_kept_from_structural_signal():
    assert kept(
        "Financial Aids",
        """
        UCAS Scholarship for International Students 2026.
        CAS-ANSO Scholarship 2026.
        Chinese Government Scholarship.
        """,
    )


def test_masters_and_phd_scholarship_is_kept():
    assert kept(
        "International Scholarship",
        """
        Scholarships are available for Master's and PhD students.
        Master's students receive tuition waiver and accommodation.
        """,
    )


def test_bachelors_and_masters_scholarship_is_kept():
    assert kept(
        "International Scholarship",
        """
        Scholarships are available for Bachelor's and Master's students.
        Master's students receive a tuition waiver and living allowance.
        """,
    )


def test_masters_computer_science_program_without_scholarship_is_rejected():
    assert not kept(
        "Master of Computer Science",
        """
        Admission requirements, curriculum, courses, faculty and
        application procedure for the Master's program.
        """,
    )


def test_bsc_software_engineering_program_without_masters_is_rejected():
    assert not kept(
        "BSc Software Engineering",
        """
        Undergraduate admission, courses, tuition and faculty information.
        """,
    )


def test_phd_computer_science_program_without_masters_is_rejected():
    assert not kept(
        "PhD Computer Science",
        """
        Doctoral admission, research areas, supervisors and PhD curriculum.
        """,
    )


def test_phd_only_scholarship_is_rejected_for_v1():
    assert not kept(
        "PhD Scholarship",
        """
        PhD scholarship with doctoral stipend and research funding.
        """,
    )


def test_bachelor_only_computing_scholarship_is_rejected_for_v1():
    assert not kept(
        "Bachelor Computer Science Scholarship",
        """
        Scholarship for undergraduate Computer Science students.
        Tuition support is available.
        """,
    )


def test_navigation_keywords_do_not_turn_academic_page_into_scholarship():
    assert not kept(
        "Majors",
        """
        <div class="program-list">
          Master Programs
          Computer Science
          Information Technology
          Engineering
        </div>
        """,
    )


def test_navigation_keywords_do_not_turn_graduate_page_into_scholarship():
    assert not kept(
        "Graduate",
        """
        Graduate education includes Master's and doctoral programs.
        The page describes admissions and degree programs.
        """,
    )


def test_page_specific_content_beats_template_noise():
    assert kept(
        "Scholarship Opportunities",
        """
        <p>Master's scholarship for Software Engineering students.</p>
        <p>Tuition waiver and accommodation are provided.</p>
        """,
        url="https://example.edu.cn/scholarships",
    )


def test_excluded_url_is_rejected_even_if_page_contains_scholarship():
    assert not kept(
        "Scholarship",
        """
        Master's scholarship. Tuition waiver and accommodation.
        """,
        url="https://example.edu.cn/about/scholarship",
    )

def test_404_scholarship_url_is_rejected():
    assert not kept(
        "404",
        """
        404
        Page Not Found
        The requested page could not be found.
        """,
        url="https://example.edu.cn/scholarship-financial-aid",
    )

def test_page_not_found_is_rejected_even_with_scholarship_url():
    assert not kept(
        "Page Not Found",
        """
        The requested page does not exist.
        """,
        url="https://example.edu.cn/scholarship/master-funding",
    )

def test_scholarship_results_page_is_rejected():
    assert not kept(
        "Announcement: Results of the 2026 Scholarship",
        """
        The results of the 2026 scholarship have been announced.
        Congratulations to the selected recipients.
        """,
        url="https://example.edu.cn/scholarship/results-2026",
    )

def test_scholarship_recipient_page_is_rejected():
    assert not kept(
        "2026 Scholarship Recipients",
        """
        The following students have been awarded the scholarship.
        """,
        url="https://example.edu.cn/scholarship/recipients-2026",
    )

def test_scholarship_issuance_regulations_are_rejected():
    assert not kept(
        "Regulations for Scholarship Issuance",
        """
        These regulations describe the rules for scholarship issuance.
        """,
        url="https://example.edu.cn/scholarship/regulations",
    )

def test_scholarship_application_announcement_is_kept():
    assert kept(
        "Announcement: 2026 Scholarship Application",
        """
        Applications are now open for the 2026 Master's Scholarship.
        Eligible international students may apply.
        Tuition waiver and accommodation are provided.
        Application deadline: 30 June 2026.
        """,
        url="https://example.edu.cn/scholarship/announcement-2026",
    )


def test_filter_returns_matched_keywords_for_kept_page():
    result = FILTER.filter(
        [
            page(
                "Master Scholarship",
                "Computer Science Master's scholarship with tuition waiver.",
            )
        ]
    )
    assert len(result) == 1
    assert "scholarship" in result[0].matched_keywords
    assert "master" in result[0].matched_keywords
    assert "computer science" in result[0].matched_keywords
