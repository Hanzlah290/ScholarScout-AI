from datetime import date
from uuid import uuid4

import pytest

from app.models.source import Source
from app.schemas.pipeline import ScholarshipExtraction, StoredPage
from app.services.validator.scholarship import ScholarshipValidator


def make_page() -> StoredPage:
    return StoredPage(
        source_id=uuid4(),
        url="https://www.example.edu.cn/scholarship/masters",
        title="Scholarship",
        path="storage/raw_pages/example.html",
        content_hash="abc",
    )


def make_source() -> Source:
    return Source(
        id=uuid4(),
        name="Example University",
        base_url="https://www.example.edu.cn",
        source_type="university",
        enabled=True,
    )


def make_extraction(**overrides) -> ScholarshipExtraction:
    data = {
        "is_scholarship": True,
        "title": "International Master's Scholarship",
        "university": "Example University",
        "country": "China",
        "degree": "Master's",
        "field": "Software Engineering",
        "funding": "Fully Funded",
        "deadline": date(2099, 1, 1),
        "requirements": ["Bachelor's degree"],
        "documents_required": ["Transcript"],
        "application_link": "https://www.example.edu.cn/apply/masters",
        "summary": "Funding for international Master's students.",
    }
    data.update(overrides)
    return ScholarshipExtraction.model_validate(data)


def test_validator_accepts_in_scope_scholarship() -> None:
    source = make_source()
    result = ScholarshipValidator().validate(make_extraction(), make_page(), source)

    assert result.status == "Open"
    assert result.country == "China"
    assert result.source_id == source.id


def test_validator_rejects_non_chinese_scholarship() -> None:
    with pytest.raises(ValueError, match="country scope"):
        ScholarshipValidator().validate(
            make_extraction(country="Japan"), make_page(), make_source()
        )

def test_validator_accepts_http_application_link_from_official_source() -> None:
    result = ScholarshipValidator().validate(
        make_extraction(
            application_link="http://apply.isc.bit.edu.cn/"
        ),
        make_page(),
        make_source(),
    )

    assert str(result.application_link) == "http://apply.isc.bit.edu.cn/"

def test_validator_accepts_https_application_link() -> None:
    result = ScholarshipValidator().validate(
        make_extraction(application_link="https://apply.example.com/masters"),
        make_page(),
        make_source(),
    )

    assert str(result.application_link).startswith("https://")

def test_validator_rejects_non_scholarship() -> None:
    with pytest.raises(ValueError, match="valid scholarship"):
        ScholarshipValidator().validate(
            make_extraction(is_scholarship=False),
            make_page(),
            make_source(),
        )


def test_validator_rejects_csc_scholarship() -> None:
    with pytest.raises(ValueError, match="CSC"):
        ScholarshipValidator().validate(
            make_extraction(
                title="Chinese Government Scholarship",
                summary="Chinese Government Scholarship for Master's students.",
            ),
            make_page(),
            make_source(),
        )


def test_validator_rejects_non_master_degree() -> None:
    with pytest.raises(ValueError, match="Master"):
        ScholarshipValidator().validate(
            make_extraction(degree="Bachelor's"),
            make_page(),
            make_source(),
        )


def test_validator_rejects_unrelated_field() -> None:
    with pytest.raises(ValueError, match="computing"):
        ScholarshipValidator().validate(
            make_extraction(field="Civil Engineering"),
            make_page(),
            make_source(),
        )





def test_validator_marks_past_deadline_closed() -> None:
    result = ScholarshipValidator().validate(
        make_extraction(deadline=date(2020, 1, 1)),
        make_page(),
        make_source(),
    )

    assert result.status == "Closed"


def test_validator_accepts_computer_science() -> None:
    result = ScholarshipValidator().validate(
        make_extraction(field="Computer Science"),
        make_page(),
        make_source(),
    )

    assert result.field == "Computer Science"


def test_validator_accepts_information_technology() -> None:
    result = ScholarshipValidator().validate(
        make_extraction(field="Information Technology"),
        make_page(),
        make_source(),
    )

    assert result.field == "Information Technology"


def test_validator_accepts_postgraduate_master_target() -> None:
    result = ScholarshipValidator().validate(
        make_extraction(
            degree="Postgraduate Master's",
            field="Computer Science and Technology",
        ),
        make_page(),
        make_source(),
    )

    assert result.degree == "Postgraduate Master's"