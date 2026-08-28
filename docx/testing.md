\# Software Testing Architecture & Verification Guide — ScholarScout AI

This document establishes the testing architecture, framework configuration, execution patterns, mocking practices, and verification checklists for **\*\*ScholarScout AI\*\***.

\---

\#\# 1\. Testing Strategy

ScholarScout AI employs a multi-layered testing strategy focused on validating the core ETL pipeline components, page pre-filtering logic, AI parsing integration, database persistence, and REST API controllers.

\`\`\`mermaid  
flowchart TD  
    subgraph Test Suite Layers  
        API\[API & Endpoint Integration Tests\]  
        Pipeline\[Pipeline & Orchestration Tests\]  
        Filter\[Page Pre-Filter & Regex Heuristic Tests\]  
        PDF\[PDF Evidence Parsing Tests\]  
        Mock\[LLM & External HTTP Mock Services\]  
    end

    API \--\> Pipeline  
    Pipeline \--\> Filter  
    Pipeline \--\> PDF  
    Filter \--\> Mock  
    PDF \--\> Mock

## **2\. Test Structure & Directory Mapping**

All backend test modules reside within the backend/tests/ directory:

Plaintext  
ScholarScout-AI/  
└── backend/  
    ├── pytest.ini                         \# Pytest root configuration  
    └── tests/  
        ├── test\_main.py                   \# FastAPI application lifespan & health endpoint tests  
        ├── test\_filter.py                 \# Pre-filter heuristic rule verification  
        ├── test\_actual\_filter.py          \# Real-world HTML content scoring tests  
        ├── test\_automation.py              \# Discovery manager & source queue state tests  
        ├── test\_connector.py              \# University web crawler connector tests  
        ├── test\_discovery\_job.py          \# APScheduler discovery task execution tests  
        ├── test\_external\_pdf.py           \# Remote PDF download and link discovery tests  
        ├── test\_models.py                 \# SQLAlchemy ORM entity model instantiation tests  
        ├── test\_pdf\_downloader.py         \# Async PDF file download & filesystem tests  
        ├── test\_pdf\_evidence\_processor.py \# PDF text extraction & evidence validation tests  
        ├── test\_pdf\_evidence\_validator.py \# Evidence threshold and rule validation tests  
        ├── test\_pdf\_extraction\_gemini.py  \# Gemini LLM prompt extraction tests (with mocks)  
        ├── test\_pipeline.py               \# End-to-end extraction pipeline runner tests  
        ├── test\_real\_crawler.py           \# Integration tests for live domain HTTP retrieval  
        ├── test\_real\_filter.py            \# Live portal pre-filtering validation  
        └── test\_scheduler.py              \# APScheduler lifecycle service tests

## **3\. Test Frameworks & Tools**

| Subsystem | Framework / Library | Version | Purpose |
| :---- | :---- | :---- | :---- |
| **Test Runner** | Pytest | v8.0+ | Primary Python test execution and assertion framework |
| **Async Test Support** | pytest-asyncio | v0.23+ | AsyncIO event loop management for async routes/services |
| **HTTP Client Mocking** | HTTPX / Pytest-Mock | Native | Mocking async network requests and external responses |
| **Browser Scraper** | Playwright | v1.40+ | Headless browser testing for dynamic JavaScript rendering |

## **4\. Running Tests**

All test commands must be executed from the backend/ directory with the virtual environment (.venv) activated.

### **Run Full Test Suite**

Bash  
cd backend  
pytest

### **Run Specific Test Modules**

Bash  
\# Test page pre-filter heuristic rules  
pytest tests/test\_filter.py

\# Test PDF evidence processor  
pytest tests/test\_pdf\_evidence\_processor.py

\# Test FastAPI main entrypoint  
pytest tests/test\_main.py

### **Run Tests with Console Output & Verbosity**

Bash  
pytest \-v \-s

## **5\. Unit Testing Patterns**

Unit tests focus on isolated class structures without invoking external network requests:

* ScholarshipPageFilter **Testing:** Evaluates keyword scoring heuristics (scholarship, international student, grant) on string payloads.  
*   
* **Evidence Validation Testing:** Assesses minimum text threshold checks and structural validation for parsed documents.  
* 

## **6\. Integration Testing**

Integration tests verify component interaction across multiple application layers:

* **Pipeline Integration (**test\_pipeline.py**):** Validates data flow from raw HTML inputs through the filter layer, mock extraction engine, and SQLAlchemy model instantiation.  
*   
* **API Route Integration (**test\_main.py**):** Tests FastAPI HTTP GET requests to /api/v1/scholarships and /api/v1/scholarships/stats.  
* 

## **7\. End-to-End & Live Crawler Testing**

* **Live Domain Crawling (**test\_real\_crawler.py**):** Contains opt-in integration tests designed to make live HTTP requests to designated .edu.cn university portals to verify DOM parser stability.  
*   
* *Note: Live tests require active internet connectivity and valid external domain availability.*  
* 

## **8\. Database Testing Behavior**

* **Session Isolation:** Integration tests leverage a temporary SQLite or PostgreSQL test session (SessionLocal).  
*   
* **Schema Initialization:** Test setups execute Base.metadata.create\_all(bind=engine) prior to running test cases to ensure isolated database tables.  
* 

## **9\. Mocking Patterns**

To prevent token consumption and avoid external API dependency during automated testing, the Gemini API and external HTTP endpoints are mocked:

### **Mocking Gemini AI Extractor (**test\_pdf\_extraction\_gemini.py**)**

Python  
from unittest.mock import AsyncMock, patch

@patch("app.services.extraction.openai\_extractor.OpenAIExtractor.extract\_scholarship")  
async def test\_gemini\_extraction\_mock(mock\_extract):  
    mock\_extract.return\_value \= {  
        "title": "Mock CSC Scholarship",  
        "university": "Tsinghua University",  
        "funding\_type": "Full",  
        "degree\_level": "Master"  
    }  
    \# Execute pipeline logic using mocked LLM response

## **10\. Test Data & Fixtures**

Test HTML snippets, PDF announcement samples, and mock database models are stored directly inside individual test files under backend/tests/:

* **Sample HTML Snippets:** Raw string representations of Chinese university scholarship announcement tables.  
*   
* **Mock Sources:** Instantiated Source SQLAlchemy objects (status='active', url='https://www.bit.edu.cn').  
* 

## **11\. Test Coverage**

Test execution configuration is managed via backend/pytest.ini:

Ini, TOML  
\[pytest\]  
testpaths \= tests  
python\_files \= test\_\*.py  
python\_classes \= Test\*  
python\_functions \= test\_\*  
asyncio\_mode \= auto

To generate a coverage report locally, install pytest-cov and execute:

Bash  
pytest \--cov=app \--cov-report=term-missing

## **12\. What Should Be Tested (Target Matrix)**

### **High Priority (Must Have Test Coverage)**

* \[x\] Pre-filtering rules (ScholarshipPageFilter) to guarantee early rejection of non-scholarship pages.  
*   
* \[x\] Deduplication logic (content\_hash) to ensure duplicate URLs are not written twice.  
*   
* \[x\] FastAPI response serialization (ScholarshipListResponse).  
*   
* \[x\] PDF downloading and text extraction handlers.  
* 

## **13\. Adding a New Test Case**

When creating a new service feature (e.g., adding a new validation rule to app/services/validator/):

1. Create a corresponding test file: backend/tests/test\_new\_feature.py.  
2.   
3. Import pytest and target modules.  
4.   
5. Use asyncio mark if testing async logic:  
6. 

Python  
import pytest  
from app.services.validator.scholarship import ScholarshipValidator

@pytest.mark.asyncio  
async def test\_scholarship\_validation\_rule():  
    validator \= ScholarshipValidator()  
    result \= await validator.validate({"title": "Valid Scholarship Title"})  
    assert result.is\_valid is True

## **14\. Pre-Merge Testing Checklist**

* \[ \] Execute standard pytest suite locally and ensure zero failures.  
*   
* \[ \] Confirm no live Gemini API keys are consumed during automated test runs (verify mocks).  
*   
* \[ \] Test database tables initialized and cleaned up cleanly.  
*   
* \[ \] Verify both async API routes and background job tasks pass unit checks.  
* 

## **15\. Testing Gaps & Recommended Improvements**

### **Existing Implementation**

* Comprehensive unit and mock integration tests for pre-filtering, PDF extraction, pipeline runner, and core API endpoints.  
* 

### **Identified Gaps & Technical Debt**

1. **Frontend End-to-End Testing:** The Next.js frontend (frontend/) currently lacks automated Playwright/Cypress UI integration tests.  
2.   
3. **Mocking Centralization:** Move inline HTML sample strings into shared fixture files under backend/tests/fixtures/.

