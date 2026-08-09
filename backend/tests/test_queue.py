from app.services.connectors.university import UniversitySourceConnector

connector = UniversitySourceConnector()

urls = [
    "https://english.bit.edu.cn/admission.html",
    "https://english.bit.edu.cn/postgraduate.html",
    "https://english.bit.edu.cn/officeofadmissions.html",
    "https://english.bit.edu.cn/2026-01/01/scholarship.html",
    "https://english.bit.edu.cn/ourstory.html",
]

print("=== PRIORITY TEST ===")

for url in urls:
    print(
        connector._priority(url, 1),
        "|",
        url,
    )