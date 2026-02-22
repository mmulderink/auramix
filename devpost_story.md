## Inspiration

Every great DJ set tells a story. You start in a smoky jazz lounge, the tempo rises, and suddenly you're tearing through a neon-lit highway at midnight. That emotional arc—the _narrative_ of a mix—is something experienced DJs craft intuitively, but it has never been something you can simply _describe in words_ and let a machine execute.

We asked ourselves: **what if you could type a cinematic vibe prompt like "From a rainy jazz club to a high-speed neon chase" and have an AI build the transition for you?**

Traditional DJ software lets you sort by BPM and key, but it knows nothing about _mood_. Streaming algorithms recommend songs you already like, but they cannot sculpt a journey across emotional landscapes. We wanted to bridge that gap—combining the semantic understanding of large language models with the mathematical rigor of vector similarity search over real audio features—to create a tool that mixes music the way a filmmaker scores a scene.

## What We Learned

**Audio feature extraction is surprisingly deep.** Using librosa to compute MFCCs (Mel-Frequency Cepstral Coefficients), chroma features, and tempo estimation taught us how much musical information can be compressed into a 512-dimensional vector. Choosing the right number of MFCC coefficients and the right segment duration (we settled on 30 s) directly impacts how "vibe-aware" the embeddings are.

**Vector databases make similarity search trivial—once your embeddings are good.** Actian VectorAI gave us sub-second cosine-similarity queries across our entire track library. The real challenge was not the database; it was ensuring the vectors we fed it actually captured perceptual similarity rather than just spectral fingerprints.

**Prompt deconstruction is an under-explored UX pattern.** Wrapping Sphinx AI as a CLI to decompose a free-text vibe prompt into structured attributes (BPM range, musical key trajectory, mood vectors) showed us that LLM reasoning can serve as a "semantic middleware" between human intent and numerical queries.

**Crossfading in the browser is non-trivial.** Managing two HTMLAudioElement instances, smoothly interpolating volumes over a configurable duration, then swapping deck references without audio glitches required careful state management in React with useRef and useCallback.

**Real-time telemetry transforms a demo into an experience.** Our "Brain Panel"—a cyberpunk-styled live log feed built with Framer Motion—lets the audience _see_ the AI think in real time. Showing Sphinx reasoning steps and Actian distance scores side-by-side turned a backend process into a visual spectacle.

## How We Built It

AuraMix is a full-stack application with four cooperating layers.

**Layer 1: Audio Ingestion Pipeline** — We scan a user-specified directory recursively for .mp3 files. For each track, we load the first 30 seconds with librosa at 22,050 Hz and extract metadata: **BPM** via beat tracking, **musical key** via a chroma-CQT argmax heuristic, and **genre** via a BPM-bracket heuristic (Ballad <70, R&B <100, Rock/Pop <120, Dance <140, EDM ≥140). We then compute 20 MFCCs, flatten them, and pad or truncate to a **512-D embedding vector**. All vectors and payloads are batch-upserted into an **Actian VectorAI** collection using the CortexClient Python SDK over gRPC with cosine distance. We also optionally write a local fallback_db.json for offline demo use.

**Layer 2: Intelligence Backend (FastAPI)** — The core endpoint is POST /api/transition. It first calls **Sphinx AI** via subprocess to deconstruct the vibe prompt into BPM, key, and three mood vectors. It then generates a deterministic 512-D query vector seeded by a hash of the prompt and vibe weight, and performs a **top-k cosine search** (k=3) against Actian VectorAI. If the database is unreachable, it falls back to a local Euclidean-distance scan over fallback_db.json. Finally, it logs the full reasoning chain and results to **Neon DB** (PostgreSQL) for history and auditability. Additional endpoints handle background ingestion with progress polling, mix history retrieval, and audio file streaming.

**Layer 3: Frontend (Next.js + Tailwind + Framer Motion)** — The UI is a dual-deck DJ interface with animated spinning vinyl, per-deck play/pause, real-time volume bars, and an equalizer visualizer. Users type vibe prompts into a prompt bar with a Dark-to-Energy slider (0–100) and hit EXECUTE. A smooth crossfader performs 40-step linear interpolation over 4 seconds, swapping audio element references at the end so the new track becomes Deck A. There is also a Music Folder input with a LINK & INGEST button and a live progress bar, plus a Neon DB Mix History panel showing past prompts and matched tracks.

**Layer 4: The Brain Panel** — This is a cyberpunk-themed, auto-scrolling telemetry feed built with Framer Motion. Each log entry is color-coded by source: cyan for Sphinx AI reasoning steps, emerald for Actian VectorAI distance results, and fuchsia for system events like ingestion and errors. Entries animate in with spring physics and include expandable JSON metadata.

**Infrastructure** — Actian VectorAI runs as a Docker container exposing gRPC on port 50051. Neon DB provides serverless PostgreSQL for the mix_history table. Sphinx AI is invoked as a local CLI binary wrapped with Python's subprocess module.

## Challenges We Faced

**Bridging text semantics and audio embeddings.** Our vibe prompts are natural language, but our track embeddings are raw MFCC features. Ideally we would use a cross-modal model (e.g., MS-CLAP) to project text and audio into a shared latent space. Under hackathon time constraints we used a deterministic hash-seeded random vector as a proxy, which still produces consistent, prompt-sensitive results—but closing this gap is our top priority for future work.

**Actian VectorAI beta SDK quirks.** The CortexClient beta does not return full payloads in search results, requiring a second client.get() call per result. We also encountered duplicate-ID collisions when re-ingesting, which we solved by dropping and recreating the collection on every ingest and using sequential integer IDs.

**Browser autoplay restrictions.** Modern browsers block audio.play() unless it originates from a user gesture. We had to restructure our crossfade logic so that the initial play always chains from a click event, and subsequent automated fades ride on that same user-activation context.

**State management during crossfades.** Swapping two HTMLAudioElement refs mid-fade while simultaneously updating React state for volumes, play/pause icons, and deck labels required precise coordination between useRef, useState, and setInterval—a single missed cleanup could leave ghost audio playing.

**Embedding dimensionality and quality trade-offs.** We experimented with different numbers of MFCCs (13 vs. 20) and different flatten/pad strategies. Too few coefficients lost timbral nuance; too many introduced noise from silent padding. We settled on 20 MFCCs truncated/padded to 512 dimensions as the best balance for our track library size.

**Fallback resilience under demo conditions.** Hackathon Wi-Fi is unpredictable. We built a full offline fallback path: if Actian is unreachable, the backend computes manual Euclidean distances over a local fallback_db.json, ensuring the demo never hard-fails regardless of network conditions.
