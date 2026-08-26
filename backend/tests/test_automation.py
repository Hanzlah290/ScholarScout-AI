import sys
import asyncio

# Ensure Windows Proactor Policy for Python 3.14
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from app.services.automation.source_validator import validate_source # Adjust import to match your crawler/validator service

async def main():
    test_url = "https://isd.pku.edu.cn/" # Or any university URL you want to test
    print(f"=== Testing Automation Layer for: {test_url} ===")
    
    try:
        # Call your scraping/crawling function directly
        result = await validate_source(test_url)
        print("Scraping successful!")
        print(f"Extracted content length: {len(result)} characters")
        print("First 300 characters of raw HTML/text:")
        print(result[:300])
    except Exception as e:
        print(f"Automation test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())