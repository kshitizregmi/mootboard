**From Sketch to Runway with Fashion Moodboard Multimodel Agent**


https://github.com/user-attachments/assets/7817b08a-f4a4-4099-9624-023763322492



Transform plain‑English fashion ideas into polished moodboards using a coordinated set of Google ADK multimodel agents. The pipeline moves from text → sketch → digital illustration → curated moodboard, and finally to Runway with a supervisor agent orchestrating each agent. 

**Highlights**
- Text → Sketch: Generates black‑and‑white concept sketches from descriptions.
- Sketch → Digital: Produces colorful digital illustrations from sketches.
- Moodboard Builder: Curates final boards from generated visuals and references.
- Runway Modeling: Takes the model in mootboard or sketch and converts that into video where model 
- Multi‑Agent Orchestration: Supervisor coordinates specialized agents end‑to‑end.

**Architecture**
- `supervisor_agent`: Plans the workflow, delegates tasks, aggregates results.
- `text_to_sketch_agent`: Turns textual briefs into pencil‑style sketches.
- `sketch_to_digital_agent`: Converts sketches into detailed digital art.
- `moodboard_agent`: Assembles moodboards from images and context.

Outputs are written to `output/` with stage subfolders (e.g., `text-to-sketch/`, `sketch-to-digital/`, `moodboard/`).

**Tech Stack**
- Google ADK + Gemini (Generative AI)
- Python 3.9+ (`google-adk`, `google-generativeai`, `google-genai`)
- Optional: Docker for reproducible runs

**Quick Start**
- Prerequisites
  - Python `3.9+` (see `.python-version`)
  - Google API key for Gemini: set `GEMINI_API_KEY` (or `GOOGLE_API_KEY`)
  - Optional: `uv` package manager, otherwise use `pip`

- Install dependencies (choose one)
  - With `uv`:
    - `uv pip install -r requirements.txt`
  - With `pip`:
    - `python -m venv .venv && . .venv/Scripts/activate` (Windows) or `source .venv/bin/activate` (Unix)
    - `pip install -r requirements.txt`

- Configure environment
  - Create `.env` and set your key:
    - `GEMINI_API_KEY=YOUR_KEY`

- Run via ADK Studio (web UI)
  - `adk web` (or `adk web --host 0.0.0.0 --port 8080`)
  - Explore and run agents from the browser.

- Run the full pipeline from CLI
  - `adk run supervisor_agent`

**Example: Sketch → Digital (Script)**
- The sample script `sketch-to-digital.py` demonstrates image + prompt generation with Gemini:
  - Place an input sketch at `dress.webp`.
  - Run: `python sketch-to-digital.py`
  - Output image: `generated_image.png`

**Project Layout**
- `supervisor_agent/`: Orchestration agent entry.
- `text_to_sketch_agent/`: Text → sketch agent.
- `sketch_to_digital_agent/`: Sketch → digital agent.
- `moodboard_agent/`: Moodboard assembly agent.
- `output/`: Artifacts per stage (created at runtime).
- `requirements.txt`: Python dependencies.
- `Dockerfile`: Containerized ADK Studio runtime.
- `pyproject.toml`: Project metadata and dependencies.

**Docker**
- Build: `docker build -t moodboard-adk .`
- Run: `docker run --rm -it -p 8080:8080 -e GEMINI_API_KEY=YOUR_KEY moodboard-adk`
- Opens ADK Studio at `http://localhost:8080` (CMD in Dockerfile runs `adk web`).

**Environment Variables**
- `GEMINI_API_KEY` or `GOOGLE_API_KEY`: Gemini key for generation.
- Optional model tuning (if your agents read them):
  - `GENAI_MODEL` (e.g., `gemini-2.0-flash-exp`)
  - `IMAGE_MODEL` (e.g., `gemini-2.5-flash-image`)

**Usage Tips**
- Describe garments, palette, textures, and references in natural language.
- For better results, include silhouette, fabric types, era/inspiration, and target vibe.
- Use the supervisor to chain stages, or run agents individually for iteration.

Troubleshooting

* Veo 3 inconsistencies: May hallucinate or mix attire/styles across frames (e.g., a kimono on European-style features or mismatched garments).
* Docs navigation: Google SDK documentation can be hard to navigate.
* Artifacts & caching: Storing and caching agent outputs via callbacks needs refinement.

**Roadmap**

**Some example outputs** 

<img width="1024" height="1024" alt="male_indian" src="https://github.com/user-attachments/assets/0e0211c9-1dfe-470f-8eef-68e31b382e6e" />
-Text to Sketch

<img width="1024" height="1024" alt="unnamed" src="https://github.com/user-attachments/assets/914f329c-7fed-453b-b0f9-9a65d4fec85c" />

-Sketch to Image

<img width="1024" height="1024" alt="generated_moodboard" src="https://github.com/user-attachments/assets/e42f7ada-9a49-4a54-bfc1-f77ae6dea3eb" />

-Image to mood board





