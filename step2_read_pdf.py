from pypdf import PdfReader

reader = PdfReader("aditi_rajawat(16).pdf")

full_text = ""
for page in reader.pages:
    full_text += page.extract_text() + "\n"

print(full_text)
print(f"\n--- Extracted {len(reader.pages)} pages, {len(full_text)} characters ---")