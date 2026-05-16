import pdfplumber
from pdf2image import convert_from_path
import pytesseract
import re

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ---------------------------
# 1. LOAD + OCR
# ---------------------------
def load_pdf(path):
    text = ""

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted

    if len(text.strip()) < 50:
        print("⚠️ Falling back to OCR...")
        images = convert_from_path(path)
        for img in images:
            text += pytesseract.image_to_string(img)

    return text


# ---------------------------
# 2. CLEAN TEXT (IMPORTANT)
# ---------------------------
def clean_text(text):
    text = re.sub(r'[^a-zA-Z0-9\s\.\-\+#]', ' ', text)
    text = re.sub(r'[^\S\n]+', ' ', text)  # Preserve newlines, replace other whitespace with space
    return text


# ---------------------------
# 3. CHUNKING
# ---------------------------
def chunk_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    return splitter.split_text(text)


# ---------------------------
# 4. EMBEDDINGS
# ---------------------------
def create_embeddings(chunks):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    return model.encode(chunks)


def create_faiss_index(embeddings):
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)

    embeddings = np.array(embeddings).astype('float32')
    index.add(embeddings)

    return index


# ---------------------------
# 5. SMART RETRIEVAL
# ---------------------------
def retrieve_chunks(query, model, index, chunks, k=5):
    query_embedding = model.encode([query]).astype('float32')
    _, indices = index.search(query_embedding, k)
    return [chunks[i] for i in indices[0]]


# ---------------------------
# 6. SECTION FILTERING
# ---------------------------
def filter_skill_chunks(chunks):
    KEYWORDS = [
        "skills", "technical skills", "technologies",
        "tools", "tech stack", "competencies"
    ]

    filtered = [
        chunk for chunk in chunks
        if any(keyword in chunk.lower() for keyword in KEYWORDS)
    ]

    return filtered if filtered else chunks


# ---------------------------
# 7. SKILL EXTRACTION (HYBRID)
# ---------------------------
def extract_skills(chunks):
    skills = set()
    
    # Common OCR corrections (lowercase input, proper case output)
    corrections = {
        "openal": "openai",
        "tensorfow": "tensorflow",
        "pythor": "python",
        "javascrpt": "javascript",
        "reactjs": "react",
        "nodejs": "node.js",
        "c++": "c++",
        "c#": "c#",
        # Add more common OCR errors as needed
    }
    
    # Proper case for known skills
    proper_case = {
        "openai": "OpenAI",
        "tensorflow": "TensorFlow",
        "python": "Python",
        "javascript": "JavaScript",
        "react": "React",
        "node.js": "Node.js",
        "c++": "C++",
        "c#": "C#",
        "html": "HTML",
        "css": "CSS",
        "sql": "SQL",
        "aws": "AWS",
        "azure": "Azure",
        "gcp": "GCP",
        "docker": "Docker",
        "kubernetes": "Kubernetes",
        "git": "Git",
        "linux": "Linux",
        "windows": "Windows",
        "macos": "macOS",
        # Add more as needed
    }
    
    non_skill_words = [
        "education", "experience", "contact", "university", "college", "school",
        "project", "achievement", "certification", "award",
        "reference", "objective", "summary", "profile",
        "location", "address", "phone", "email", "linkedin", "github",
        "portfolio", "website", "date", "month", "year",
        "name", "resume", "cv",
        "grade", "percentage", "cgpa",
        "about me", "work experience"
    ]
    
    # Valid single-word skills (lowercase for matching)
    valid_single_skills = {
        "python", "java", "javascript", "c++", "c#", "html", "css", "sql", "git",
        "aws", "azure", "gcp", "docker", "kubernetes", "linux", "windows", "macos",
        "react", "node.js", "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn",
        "mongodb", "mysql", "postgresql", "redis", "elasticsearch", "kafka", "spark",
        "hadoop", "airflow", "jenkins", "github", "bitbucket", "jira", "confluence"
    }
    
    for chunk in chunks:
        # Clean chunk: remove non-alphanumeric except spaces, dots, hyphens, plus, hash
        chunk = re.sub(r'[^a-zA-Z0-9\s\.\-\+#]', ' ', chunk)
        chunk = chunk = re.sub(r'[^\S\n]+', ' ', chunk).strip()
        
        # Split camelCase to separate words
        chunk = re.sub(r'([a-z])([A-Z])', r'\1 \2', chunk)
        
        # Split into potential skills on commas, slashes, newlines, ' and '
        parts = re.split(r'(?:,| and |/|\n)', chunk)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            part_lower = part.lower()
            
            # Apply OCR corrections
            for wrong, correct in corrections.items():
                part_lower = part_lower.replace(wrong, correct)
            
            # Normalize case
            part = proper_case.get(part_lower, part_lower.title())
            
            # Filter length
            if len(part) < 2 or len(part) > 50:
                continue
            
            # Skip if contains non-skill words
            if part_lower in non_skill_words:
                continue
            
            # Skip if looks like date or number-heavy
            if re.search(r'\d{4}', part) or len(re.findall(r'\d', part)) > len(part) / 2:
                continue
            
            # Skip single words unless they are valid skills
            words = part.split()
            if len(words) == 1 and part_lower not in valid_single_skills:
                continue
            
            skills.add(part)
    
    return sorted(skills)

COMMON_NON_TECH = [
    "team", "communication", "collaboration",
    "management", "leadership"
]

def filter_technical_skills(skills):
    filtered = []

    for skill in skills:
        if not any(word in skill.lower() for word in COMMON_NON_TECH):
            filtered.append(skill)

    return filtered

# ---------------------------
# MAIN
# ---------------------------
if __name__ == "__main__":
    print("🚀 Script started...\n")

    file_path = "data/Dhaani_Jain_resume.pdf"

    # Step 1: Load
    text = load_pdf(file_path)

    # Step 2: Clean
    text = clean_text(text)

    # Step 3: Chunk
    chunks = chunk_text(text)

    # Step 4: Filter skill sections
    chunks = filter_skill_chunks(chunks)

    print(f"✅ Total relevant chunks: {len(chunks)}\n")

    # Step 5: Embeddings
    embeddings = create_embeddings(chunks)
    index = create_faiss_index(embeddings)

    # Step 6: Retrieval
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query = "technical skills programming languages tools frameworks"

    results = retrieve_chunks(query, model, index, chunks)
    skills = extract_skills(results)
    skills = filter_technical_skills(skills)

    print("📄 Retrieved Chunks:\n")
    for i, r in enumerate(results):
        print(f"--- Chunk {i+1} ---\n{r}\n")

    print("\n🤖 EXTRACTED SKILLS:\n")
    for s in skills:
        print(f"- {s}")