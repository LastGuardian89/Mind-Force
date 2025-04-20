import fitz  # PyMuPDF
import requests
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_text_from_url_pdf(url):
    response = requests.get(url)
    with open("temp.pdf", 'wb') as f:
        f.write(response.content)
    return extract_text_from_uploaded_pdf("temp.pdf")

def extract_text_from_uploaded_pdf(path='temp.pdf'):
    doc = fitz.open(path)
    return "\n".join([page.get_text() for page in doc])

def find_relevant_passages(text, question, k=5):
    chunks = text.split("\n\n")
    embeddings = model.encode(chunks, convert_to_tensor=True)
    question_emb = model.encode(question, convert_to_tensor=True)
    top_k = util.semantic_search(question_emb, embeddings, top_k=k)[0]
    return "\n".join([chunks[idx['corpus_id']] for idx in top_k])