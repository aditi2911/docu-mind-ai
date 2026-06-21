from pypdf import PdfReader
from google import genai
from dotenv import load_dotenv
import os
import numpy as np

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

reader = PdfReader("aditi_rajawat(16).pdfp")
full_text = ""
for page in reader.pages:
    full_text += page.extract_text() + "\n"

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

chunks = chunk_text(full_text)

def get_embedding(text):
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )
    return np.array(result.embeddings[0].values)

print("Embedding document...")
chunk_embeddings = [get_embedding(c) for c in chunks]
print("Ready.\n")

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def search(question, top_k=3):
    q_embedding = get_embedding(question)
    scores = [cosine_similarity(q_embedding, ce) for ce in chunk_embeddings]
    ranked = sorted(zip(scores, chunks), reverse=True)
    return [chunk for score, chunk in ranked[:top_k]]

def answer_question(question):
    relevant_chunks = search(question)
    context = "\n---\n".join(relevant_chunks)

    prompt = f"""Answer the question using ONLY the context below.
If the answer isn't in the context, say "I don't know based on this document."

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

# ---- Interactive loop ----
print("Ask questions about your document (type 'exit' to quit).\n")
while True:
    q = input("Your question: ")
    if q.lower() == "exit":
        break
    print(f"\n{answer_question(q)}\n")