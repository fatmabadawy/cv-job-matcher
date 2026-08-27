from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
import pickle

MODEL_NAME = "all-MiniLM-L6-v2"
INDEX_PATH = "faiss_index/jobs.index"
IDS_PATH = "faiss_index/job_ids.pkl"
DIM = 384

_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_text(text: str) -> np.ndarray:
    """Embed a single text string into a normalized float32 vector."""
    vec = get_model().encode([text], convert_to_numpy=True)[0].astype("float32")
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec


def build_index(db) -> int:
    """Build/update the FAISS index with unindexed jobs using cosine similarity."""
    import models as m
    
    os.makedirs("faiss_index", exist_ok=True)

    ids = []
    if os.path.exists(INDEX_PATH) and os.path.exists(IDS_PATH):
        index = faiss.read_index(INDEX_PATH)
        with open(IDS_PATH, "rb") as f:
            ids = pickle.load(f)
    else:
        index = faiss.IndexFlatIP(DIM)

    indexed_set = set(ids)
    all_jobs = db.query(m.Job).all()
    jobs_to_index = [j for j in all_jobs if j.id not in indexed_set]

    if not jobs_to_index:
        return 0

    texts = [
        f"Title: {j.title} | Company: {j.company} | Requirements: {j.requirements or ''} | Description: {(j.description or '')[:400]}"
        for j in jobs_to_index
    ]
    vectors = get_model().encode(texts, convert_to_numpy=True, show_progress_bar=False).astype("float32")
    faiss.normalize_L2(vectors)

    index.add(vectors)
    ids.extend([j.id for j in jobs_to_index])

    faiss.write_index(index, INDEX_PATH)
    with open(IDS_PATH, "wb") as f:
        pickle.dump(ids, f)

    for j in jobs_to_index:
        j.embedding_status = "done"
    db.commit()
    return len(jobs_to_index)


def search_similar(query_vector: np.ndarray, top_k: int = 20) -> list[int]:
    """Search the FAISS index using cosine similarity. Returns list of job IDs."""
    if not os.path.exists(INDEX_PATH) or not os.path.exists(IDS_PATH):
        return []
    index = faiss.read_index(INDEX_PATH)
    with open(IDS_PATH, "rb") as f:
        ids = pickle.load(f)
    if not ids:
        return []
    q_vec = np.array([query_vector]).astype("float32")
    faiss.normalize_L2(q_vec)
    k = min(top_k, len(ids))
    distances, indices = index.search(q_vec, k)
    result = []
    for i in indices[0]:
        if i != -1 and i < len(ids):
            result.append(ids[i])
    return result
