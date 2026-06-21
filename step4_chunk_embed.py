from pypdf import PdfReader
from google import genai
from dotenv import load_dotenv
import os
import numpy as np

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ---- 1. Extract text from PDF ----
reader = PdfReader("aditi_rajawat(16).pdf")
full_text = ""
for page in reader.pages:
    full_text += page.extract_text() + "\n"

# ---- 2. Chunk the text ----
def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap   # overlap keeps context between chunks
    return chunks

chunks = chunk_text(full_text)
print(f"Document split into {len(chunks)} chunks.\n")

# ---- 3. Embed every chunk ----
def get_embedding(text):
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )
    return np.array(result.embeddings[0].values)

print("Embedding chunks...")
chunk_embeddings = [get_embedding(c) for c in chunks]
print("Done embedding.\n")

# ---- 4. Cosine similarity function ----
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# ---- 5. Search: find most relevant chunks for a question ----
def search(question, top_k=2):
    q_embedding = get_embedding(question)
    scores = [cosine_similarity(q_embedding, ce) for ce in chunk_embeddings]
    ranked = sorted(zip(scores, chunks), reverse=True)
    return ranked[:top_k]

# ---- 6. Try it ----
question = "What projects has this person built?"
results = search(question)

print(f"Top matching chunks for: '{question}'\n")
for score, chunk in results:
    print(f"Score: {score:.3f}")
    print(chunk)
    print("---")