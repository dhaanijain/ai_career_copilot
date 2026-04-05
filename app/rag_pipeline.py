import pdfplumber
from pdf2image import convert_from_path
import pytesseract
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Set tesseract path (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def load_pdf(path):
    text = ""

    # Step 1: Try pdfplumber
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            extracted = page.extract_text()
            print(f"[DEBUG] pdfplumber Page {i}: {extracted}")
            
            if extracted:
                text += extracted

    # Step 2: Fallback to OCR if empty
    if len(text.strip()) < 50:
        print("⚠️ Falling back to OCR...")

        images = convert_from_path(path, poppler_path=r"C:\Release-25.12.0-0\poppler-25.12.0\Library\bin")
        ocr_text = ""

        for i, img in enumerate(images):
            extracted = pytesseract.image_to_string(img)
            print(f"[DEBUG] OCR Page {i}: {extracted}")
            ocr_text += extracted

        return ocr_text

    return text

from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    
    chunks = splitter.split_text(text)
    return chunks

def create_embeddings(chunks):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(chunks)
    return embeddings

def create_faiss_index(embeddings):
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)

    embeddings = np.array(embeddings).astype('float32')
    index.add(embeddings)  # type: ignore

    return index

def retrieve_chunks(query, model, index, chunks, k=3):
    # Convert query to embedding
    query_embedding = model.encode([query]).astype('float32')

    # Search in FAISS index
    distances, indices = index.search(query_embedding, k)

    # Get relevant chunks
    results = [chunks[i] for i in indices[0]]

    return results

from transformers import pipeline

generator = pipeline(
    "text-generation",
    model="google/flan-t5-small"
)

def generate_answer(query, retrieved_chunks):
    context = "\n".join(retrieved_chunks[:2])  # only top 2 chunks

    prompt = f"""
    Extract the answer from the resume.

    Resume:
    {context}

    Question: {query}

    Answer:
    """

    result = generator(prompt, max_new_tokens=100)

    return result[0]['generated_text']

if __name__ == "__main__":
    print("🚀 Script started...")

    file_path = "data/Dhaani_Jain_resume.pdf"
    print(f"[DEBUG] Loading file from: {file_path}")

    resume_text = load_pdf(file_path)

    chunks = chunk_text(resume_text)

    print(f"\n✅ Total chunks created: {len(chunks)}\n")

    print("🔹 First chunk:\n")
    print(chunks[0])

    print("\n🔹 Second chunk:\n")
    print(chunks[1] if len(chunks) > 1 else "Only one chunk")
    
    embeddings = create_embeddings(chunks)
    print(f"\n✅ Embeddings shape: {embeddings.shape}")

    index = create_faiss_index(embeddings)
    print("✅ FAISS index created")
    
        # --- Retrieval test ---
    query = "What skills does this person have?"

    print("\n🔍 Query:", query)

    model = SentenceTransformer('all-MiniLM-L6-v2')

    results = retrieve_chunks(query, model, index, chunks)

    print("\n📄 Retrieved Chunks:\n")

    for i, res in enumerate(results):
        print(f"--- Result {i+1} ---")
        print(res)
        print()
        
    answer = generate_answer(query, results)

    print("\n🤖 FINAL ANSWER:\n")
    print(answer)