from pathlib import Path

from pypdf import PdfReader


PDF_FILE = Path("storage/test_pdfs/bit_admission_book_2026.pdf")


def main():
    print("=== PDF EXTRACTION TEST ===")
    print("File:", PDF_FILE)
    print()

    if not PDF_FILE.exists():
        print("ERROR: PDF file does not exist.")
        return

    print("File size:", PDF_FILE.stat().st_size)
    print()

    reader = PdfReader(str(PDF_FILE))

    print("Pages:", len(reader.pages))
    print()

    extracted_pages = 0
    total_characters = 0

    for index, page in enumerate(reader.pages):
        text = page.extract_text() or ""

        if text.strip():
            extracted_pages += 1
            total_characters += len(text)

        print(
            f"Page {index + 1}: "
            f"{len(text)} characters"
        )

    print()
    print("Pages with text:", extracted_pages)
    print("Total extracted characters:", total_characters)
    print()

    print("=== FIRST EXTRACTED TEXT ===")
    print()

    for index, page in enumerate(reader.pages[:3]):
        text = page.extract_text() or ""

        print(f"--- PAGE {index + 1} ---")
        print(text[:2000])
        print()


if __name__ == "__main__":
    main()
