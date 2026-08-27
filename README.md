# 🎛️ JobSignal AI — Autonomous AI CV-to-Job Matching Control Room

> **JobSignal AI** is an autonomous, data-driven career control room that parses candidate resume signals, aggregates real-time software engineering job listings across **5 major global job portals** (LinkedIn, Arbeitnow, WeWorkRemotely, Remotive, RemoteOK), and computes ranked, scored job matches using **FAISS vector cosine similarity** and **Groq LLM batched reranking**.

---

## 🌟 Key Features

### 1. 🌐 5-Source Real Web Job Aggregator
- **LinkedIn Public Scraper**: Real live job listings from top tech companies (Apple, Amazon, JPMorgan Chase, Cadence, Traveloka, etc.) with direct `https://linkedin.com/jobs/view/...` original posting links.
- **Arbeitnow API**: Global software engineering positions.
- **WeWorkRemotely RSS**: Real remote programming jobs.
- **Remotive API**: Software development listings with HTML description cleaning.
- **RemoteOK API**: Title-filtered remote developer positions with non-tech blocklists.
- **Total Indexed**: **220+ real live tech jobs** in vector space.

### 2. 🧮 Dual Vector Retrieval + LLM Reranking Architecture
- **Stage 1 (FAISS Vector Retrieval)**: Candidate CV is embedded using `all-MiniLM-L6-v2` (384-dimensional space) into `FAISS IndexFlatIP` using L2-normalized cosine similarity.
- **Stage 2 (Groq LLM Reranking)**: Top candidates are evaluated via batched Groq LLM API (`openai/gpt-oss-20b` — 0.7s latency) to produce job-specific match scores (0–100%) and short human-readable reasons.

### 3. 🎨 Precision Control Room Frontend UI
- **Graphite Dark Theme**: `#14161A` deep graphite background with `#1C1F26` lifted panel surfaces.
- **Monospace Tabular Numerals**: `JetBrains Mono` tabular font formatting for all percentages, scores, and counters.
- **Signature Score Gauge Component (`<ScoreGauge />`)**: Circular SVG ring gauge indicating score percentage cleanly across cards and detail panels.
- **Multi-Filter Bar**:
  - **Location Search**: Filter jobs by city/country/region (e.g. `Germany`, `Remote`, `United States`, `Berlin`, `Cairo`, `India`).
  - **Work Mode Filter**: Toggle `Remote`, `Onsite`, or `Hybrid`.
  - **Website Source Filter**: Filter explicitly by `LinkedIn`, `Arbeitnow`, `WeWorkRemotely`, `Remotive`, `RemoteOK`, or `All`.

### 4. ⚡ AI Career Acceleration Tools
- **Tailor My CV**: Generates optimized resume summary, reordered technical skills, and tailored accomplishment bullet points. Includes **Copy to Clipboard** and **Download (.txt)**.
- **Skill Gap Analysis**: Identifies missing vs partial skill requirements with mitigation advice.
- **ATS Keyword Check**: Pure Groq LLM analysis comparing CV text to job requirements, returning real technical matched/missing keywords without web boilerplate filler terms.
- **Cover Letter Generator**: 4-paragraph tailored cover letter with 1-click copy.
- **Interview Coach**: Technical interview Q&A prep tailored to candidate background and role.

### 5. 📋 Application Pipeline (Kanban Board)
- Track active position applications across 5 stages: `Applied`, `Screening`, `Interview`, `Offer Accepted`, and `Rejected`.

---

## 🛠️ Tech Stack & Architecture

```
React 19 + Vite Frontend (Port 5173)
       │  JWT / HTTP Requests
FastAPI Backend (Port 8000)
   ├── SQLite / PostgreSQL Database
   ├── FAISS Vector Index (IndexFlatIP, 384-dim)
   ├── SentenceTransformers (all-MiniLM-L6-v2)
   ├── Multi-Source Web Scrapers (BeautifulSoup4, Requests)
   └── Groq LLM API (openai/gpt-oss-20b)
```

| Component | Technology Used |
|-----------|-----------------|
| **Backend Framework** | FastAPI (Python 3.11) |
| **Database & ORM** | SQLite (with Postgres fallback) + SQLAlchemy |
| **Embeddings Engine** | `sentence-transformers/all-MiniLM-L6-v2` |
| **Vector Database** | `faiss-cpu` (`IndexFlatIP`, Cosine Similarity) |
| **LLM Reranker & AI** | Groq SDK (`openai/gpt-oss-20b`) |
| **Web Scrapers** | Requests, BeautifulSoup4, XML Parser |
| **Frontend Framework** | React 19, Vite, React Router DOM v7 |
| **Icons & Typography** | Lucide React, Space Grotesk, Plus Jakarta Sans, JetBrains Mono |

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- A free **Groq API Key** from [console.groq.com](https://console.groq.com/)

---

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your Groq API Key
echo "GROQ_API_KEY=gsk_your_groq_api_key_here" > .env
echo "JWT_SECRET=super_secret_jwt_key_123" >> .env

# Run server
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

- Backend API: `http://127.0.0.1:8000`
- Interactive Swagger Docs: `http://127.0.0.1:8000/docs`
- Health Check: `http://127.0.0.1:8000/health`

---

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

- Web App UI: `http://localhost:5173`

---

## 💻 Database Maintenance & Automated Testing

### Rescrape Live Web Jobs & Rebuild FAISS Index
To purge existing listings, scrape fresh jobs from LinkedIn, Arbeitnow, Remotive, WeWorkRemotely & RemoteOK, and build vector embeddings:

```powershell
cd backend
.\venv\Scripts\python.exe purge_and_rescrape.py
```

### Run Full End-to-End Test Suite
To execute full automated verification tests across all 8 system endpoints and AI tools:

```powershell
cd backend
.\venv\Scripts\python.exe test_all.py
```

---

## 📌 API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Server health check |
| `POST` | `/auth/signup` | User signup & JWT generation |
| `POST` | `/auth/login` | User login & JWT validation |
| `GET` | `/auth/me` | Fetch logged-in user profile |
| `POST` | `/cv/upload` | Upload PDF/DOCX/TXT resume & extract candidate profile |
| `POST` | `/match/run` | Execute FAISS vector search + Groq LLM reranking |
| `GET` | `/match/results` | Fetch computed job matches with score & full details |
| `POST` | `/features/tailor-cv` | Generate job-tailored summary, skills & experience bullets |
| `POST` | `/features/gap-analysis` | Perform skill gap analysis |
| `POST` | `/features/ats-check` | Execute LLM ATS keyword compatibility check |
| `POST` | `/features/cover-letter` | Generate tailored cover letter |
| `POST` | `/features/interview-prep` | Generate technical interview Q&A prep |
| `GET` | `/applications` | List tracked Kanban application stages |
| `POST` | `/applications` | Track job application in pipeline |
| `PATCH` | `/applications/{id}` | Update application stage status |
| `DELETE` | `/applications/{id}` | Remove tracked application |
| `POST` | `/admin/scrape` | Trigger multi-site web scrapers |
| `POST` | `/admin/build-index` | Rebuild FAISS vector index |

---

## 📜 License

Distributed under the **MIT License**. Free for educational and commercial use.
