# AuraMix 🪩

AuraMix is a **Narrative DJ Application** built to seamlessly transition between tracks using semantic vibe prompts (e.g., "From a rainy jazz club to a high-speed neon chase"). 

## 🚀 Tech Stack
- **Frontend**: Next.js (App Router), Tailwind CSS, Framer Motion
- **Backend**: FastAPI (Python 3.11)
- **Audio Engine**: Tone.js (via Frontend)
- **Vector DB**: Actian VectorAI (via Docker: `williamimoh/actian-vectorai-db:1.0b`)
- **Relational DB**: Neon DB (PostgreSQL)
- **Logic Engine**: Sphinx AI (CLI wrapped in Python)

## 📂 Generated Files

1. **`backend/main.py`**: The FastAPI server. Wraps Sphinx AI CLI to deconstruct the vibe prompts and logs reasoning to Neon DB.
2. **`backend/ingest.py`**: A python script using `librosa` to convert local MP3 files into 512-dimension vector embeddings and push them into the Actian VectorAI database.
3. **`frontend/components/BrainPanel.tsx`**: A glowing, cyberpunk-themed React / Framer Motion component describing real-time Sphinx reasoning and Actian distances.

## 🛠 Setup Instructions

### 1. Actian VectorAI Setup
```bash
docker run -p 27832:27832 williamimoh/actian-vectorai-db:1.0b
```
*(Ensure `ACTIAN_URL` in `ingest.py` matches your port bindings).*

### 2. Neon DB Setup
Get your connection string from Neon.tech and export it:
```bash
export NEON_DB_URL="postgresql://user:password@endpoint..."
```

### 3. Backend Execution
```bash
cd backend
pip install fastapi uvicorn pydantic psycopg2 librosa numpy

# To ingest tracks:
# Place some .mp3 files in ./backend/audio_samples/
python ingest.py

# To start the API:
python main.py
```

### 4. Frontend Integration
Ensure you have `framer-motion` installed:
```bash
npm install framer-motion clsx tailwind-merge
```
Import `<BrainPanel />` into your main deck view for the live telemetry stream!
