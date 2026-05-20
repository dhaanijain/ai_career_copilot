# 🚀 AI Career Copilot

AI Career Copilot is an AI-powered resume analysis, skill extraction, and job matching platform that intelligently processes resumes — including image-based and Canva-generated PDFs — using OCR, NLP, semantic embeddings, vector similarity search, and AI-driven retrieval pipelines.

The project is designed to solve one of the biggest real-world problems in recruitment and career platforms:

> Extracting meaningful technical information from noisy, unstructured resumes and intelligently matching candidates with relevant jobs.

Unlike traditional keyword-based ATS systems, AI Career Copilot combines:
- OCR-based document understanding
- NLP preprocessing
- Semantic embeddings
- Vector databases (FAISS)
- Intelligent retrieval pipelines
- Skill extraction and normalization
- Resume-to-job matching

This enables the system to work across multiple resume formats while handling OCR noise, unstructured layouts, and semantic understanding of skills.

---

# ✨ Features

## 📄 Resume Parsing
- Supports PDF resumes
- Handles text-based PDFs
- Supports image-based resumes
- Works with Canva-generated resumes
- OCR fallback for scanned resumes

---

## 🧠 AI-Powered Skill Extraction
- Extracts technical skills intelligently
- Uses semantic retrieval instead of plain keyword search
- Removes noisy/non-technical content
- Handles OCR mistakes
- Deduplicates extracted skills
- Normalizes extracted technologies

---

## 🔍 Semantic Search with FAISS
- Converts resume chunks into embeddings
- Stores embeddings in a FAISS vector index
- Retrieves relevant resume sections using semantic similarity

---

## 📊 Resume vs Job Description Matching
- Compare resume skills with job descriptions
- Calculate semantic match score
- Detect missing skills
- Identify matching technologies
- Generate improvement suggestions

Example:

```text
Resume Match Score: 82%

✅ Matching Skills:
- Python
- TensorFlow
- SQL

❌ Missing Skills:
- Docker
- Kubernetes
- AWS
```

---

## 💼 AI Job Recommendation System (Planned)
The future version of the system will:
- Recommend jobs based on resume skills
- Fetch live job listings using APIs
- Rank jobs using semantic similarity
- Identify career gaps
- Suggest learning paths

---

## 🌐 Streamlit Web Application (Planned)
- Resume upload UI
- Job description upload
- Live skill extraction
- Match score visualization
- Interactive dashboards

---

# 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core development |
| pdfplumber | PDF text extraction |
| pytesseract | OCR support |
| pdf2image | PDF-to-image conversion |
| Sentence Transformers | Semantic embeddings |
| FAISS | Vector similarity search |
| LangChain Text Splitter | Chunking pipeline |
| NumPy | Embedding processing |
| Regex / NLP | Cleaning and filtering |
| Streamlit (Planned) | Web UI |
| Adzuna API (Planned) | Job recommendation engine |

---

# 🤖 AI Concepts Used

This project incorporates several AI, NLP, and Information Retrieval concepts:

## Natural Language Processing (NLP)
- Text preprocessing
- Cleaning and normalization
- Entity filtering
- Skill extraction

---

## Semantic Embeddings
- Resume chunks converted into vector embeddings
- Semantic understanding of resume content
- Context-aware retrieval

---

## Vector Databases
- FAISS vector index
- Similarity-based retrieval
- Efficient nearest-neighbor search

---

## Retrieval-Augmented Processing
- Retrieve relevant resume sections
- Process only meaningful chunks
- Improve extraction accuracy

---

## OCR-Based Document Intelligence
- Handles scanned/image-based resumes
- Supports Canva-generated resumes
- Extracts information from non-selectable PDFs

---

## AI Recommendation Systems (Planned)
- Resume-to-job similarity scoring
- Semantic ranking of jobs
- Skill-gap analysis
- Career recommendations

---

# 🏗️ Project Architecture

```text
PDF Resume
    ↓
Text Extraction (pdfplumber)
    ↓
OCR Fallback (Tesseract)
    ↓
Text Cleaning & Normalization
    ↓
Chunking (LangChain)
    ↓
Sentence Embeddings
    ↓
FAISS Vector Index
    ↓
Semantic Retrieval
    ↓
Skill Extraction & Filtering
    ↓
Resume vs JD Matching
    ↓
Job Recommendations (Planned)
```

---

# 📁 Folder Structure

```text
ai_career_copilot/
│
├── app/
│   └── rag_pipeline.py
│
├── data/
│   └── resume.pdf
│
├── requirements.txt
├── README.md
├── .gitignore
│
└── venv/
```

---

# ⚙️ Installation Guide

## 1. Clone the Repository

```bash
git clone <your-repository-link>
cd ai_career_copilot
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔥 OCR Setup

This project uses Tesseract OCR for image-based resumes.

---

## Windows Setup

Download:
https://github.com/UB-Mannheim/tesseract/wiki

After installation:

```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

---

## macOS Setup

```bash
brew install tesseract
brew install poppler
```

---

## Linux Setup

```bash
sudo apt install tesseract-ocr
sudo apt install poppler-utils
```

---

# ▶️ Running the Project

Place your resume inside the `data/` folder.

Example:

```text
/data/resume.pdf
```

Run:

```bash
python app/rag_pipeline.py
```

---

# 💻 Example Output

```text
🤖 EXTRACTED SKILLS:

- Python
- Java
- TensorFlow
- PyTorch
- SQL
- Git
- GitHub
- Figma
- Machine Learning
- Data Structures
- Object Oriented Programming
```

---

# 🧩 Challenges Solved

## Problem 1: Canva/Image-Based PDFs
Many resumes contain non-selectable text.

### Solution
Implemented OCR fallback using:
- pdf2image
- pytesseract

---

## Problem 2: OCR Noise

OCR introduced issues like:

```text
OpenAI → OpenAl
PyTorch → Py Torch
```

### Solution
Added normalization and OCR correction logic.

---

## Problem 3: Noisy Extraction

Initial extraction included:
- Education
- Contact information
- Grades
- Random phrases

### Solution
Implemented:
- semantic retrieval
- technical keyword filtering
- strict non-skill filtering

---

## Problem 4: Resume Format Variations

Different resumes use:
- different layouts
- bullets
- columns
- custom formatting

### Solution
Built a generalized extraction pipeline instead of hardcoded parsing.

---

# 🚀 Future Improvements

## 🌐 Streamlit Web App
- Upload resume through UI
- Upload job description
- Visualize match score
- Interactive dashboard

---

## 📊 Resume vs Job Matching
- Compare resume with multiple jobs
- Rank matching jobs
- Missing skill analysis
- ATS optimization suggestions

---

## 💼 Job Recommendation Engine
Planned integration with:
- Adzuna API
- JSearch API

Features:
- Live job recommendations
- Semantic job ranking
- AI-powered career matching

---

## 🧠 LLM Integration
- AI-generated resume feedback
- Resume summarization
- Career recommendations
- AI interview preparation

---

## ☁️ Deployment
- Streamlit Cloud
- Hugging Face Spaces
- Docker
- AWS/GCP deployment

---

# 📚 Learning Outcomes

This project helped explore:
- NLP pipelines
- Vector databases
- Semantic embeddings
- OCR systems
- Document intelligence
- Retrieval-Augmented Generation concepts
- AI recommendation systems
- Resume parsing architectures
- Semantic search systems

---

# 🌍 Real-World Applications

This system is similar to technologies used in:
- ATS (Applicant Tracking Systems)
- AI recruitment platforms
- HR-tech systems
- Resume screening tools
- Talent intelligence platforms
- AI career recommendation engines

---

# 👨‍💻 Author

## Dhaani Jain

Computer Science undergraduate focused on:
- AI Systems
- NLP
- Machine Learning
- Software Engineering
- Intelligent Automation

### LinkedIn
https://www.linkedin.com/in/dhaani-jain-a42886286/

### GitHub
https://github.com/dhaanijain

---

# 📄 License

This project is open-source and available under the MIT License.