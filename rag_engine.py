from pypdf import PdfReader
from google import genai
from dotenv import load_dotenv
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, PayloadSchemaType
import uuid
import time

load_dotenv()
genai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

COLLECTION_NAME = "documents"
VECTOR_SIZE = 3072
_qdrant_client = None


def get_qdrant_client():
    global _qdrant_client
    if _qdrant_client is not None:
        return _qdrant_client

    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    print(f"Connecting to Qdrant at: {qdrant_url}")

    for attempt in range(3):
        try:
            if qdrant_url and qdrant_api_key:
                client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key, check_compatibility=False, timeout=25)
            elif qdrant_url:
                client = QdrantClient(url=qdrant_url, check_compatibility=False, timeout=25)
            else:
                client = QdrantClient(host="localhost", port=6333, check_compatibility=False)
            client.get_collections()
            print("Connected to Qdrant successfully.")

            if not client.collection_exists(COLLECTION_NAME):
                client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
                )

            try:
                client.create_payload_index(
                    collection_name=COLLECTION_NAME,
                    field_name="filename",
                    field_schema=PayloadSchemaType.KEYWORD
                )
                print("Payload index on 'filename' ensured.")
            except Exception as idx_err:
                print(f"Index note: {idx_err}")

            _qdrant_client = client
            return client

        except Exception as e:
            print(f"Qdrant attempt {attempt+1}/3: {e}")
            time.sleep(1)

    raise RuntimeError("Could not connect to Qdrant")


def extract_text_from_pdf(filepath):
    reader = PdfReader(filepath)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def get_embedding(text):
    result = genai_client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )
    return result.embeddings[0].values


def process_document(filepath, filename):
    qdrant = get_qdrant_client()
    text = extract_text_from_pdf(filepath)
    chunks = chunk_text(text)
    points = []
    for chunk in chunks:
        embedding = get_embedding(chunk)
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={"filename": filename, "text": chunk}
            )
        )
    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
    return {"chunk_count": len(chunks)}


def search(question, filename, top_k=6):
    qdrant = get_qdrant_client()
    q_embedding = get_embedding(question)
    results = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=q_embedding,
        query_filter={
            "must": [{"key": "filename", "match": {"value": filename}}]
        },
        limit=top_k
    )
    return [point.payload.get("text", "") for point in results.points if point.payload]


def answer_question(question, filename):
    relevant_chunks = search(question, filename)
    context = "\n---\n".join(relevant_chunks)
    prompt = f"""Answer the question using ONLY the context below.
If the answer isn't in the context, say "I don't know based on this document."

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""
    response = genai_client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )
    return response.text