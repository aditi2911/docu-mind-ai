from pypdf import PdfReader
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Step 1: Extract text from PDF
reader = PdfReader("aditi_rajawat(16).pdf")
full_text = ""
for page in reader.pages:
    full_text += page.extract_text() + "\n"

# Step 2: Ask a question, using the PDF text as context
question = "What is the person's current role?"  # You can change this question as needed

prompt = f"""Answer the question using ONLY the information in the document below.
If the answer isn't in the document, say "I don't know based on this document."

DOCUMENT:
{full_text}

QUESTION: {question}

ANSWER:"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

print(response.text)