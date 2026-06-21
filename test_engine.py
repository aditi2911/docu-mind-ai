from rag_engine import process_document, answer_question

data = process_document("aditi_rajawat(16).pdf", "test_cache.pkl")
print(answer_question("What projects has this person built?", data["chunks"], data["embeddings"]))