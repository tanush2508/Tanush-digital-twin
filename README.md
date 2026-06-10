# Digital Twin MVP

A grounded professional digital twin of **Tanush Korgaokar**, built as a personal project.

This project lets someone ask questions about my background, projects, technical strengths, work style, and current focus through a chat interface. The system answers from a structured memory layer, cites the supporting context, and exposes its reasoning path in debug mode so the behavior is easier to inspect.

## Chosen deep dive

**Response Quality**

I chose to go deep on response quality instead of trying to fully build integrations, auth, or sharing. The part that interested me most here was making the twin more trustworthy. That meant improving routing, grounding, temporal awareness, unsupported question handling, and overall observability.

## What the product does

The app supports questions like:

- What project best shows your production AI engineering skills?
- Tell me about RepaintWiz
- What are your technical strengths?
- What are you focused on right now?
- What were you working on recently?

The twin answers using only the memory I provided. It also shows source snippets in the UI, and in debug mode it shows the planner output, retrieved evidence, verifier decision, final policy action, and latency timings.

## Core features

- Interactive chat UI
- Grounded responses based on local memory
- Layered memory with long term, current, and archive context
- Planner, retrieval, responder, verifier pipeline
- Source backed answers in the UI
- Debug drawer for testing and observability
- Evaluation harness for response quality
- Memory lifecycle script for current to archive to long term flow

## Architecture

### 1. Layered memory

The system separates memory by role instead of putting everything into one flat knowledge base.

**Long term memory**
This stores the stable parts of the twin:
- bio
- experience
- project writeups
- preferences
- writing style
- structured profile facts

**Current state memory**
This stores what is active right now:
- current focus
- active role search
- current priorities

**Historical archive**
This stores context that used to be current, but should no longer be treated as active:
- recent interview prep
- earlier focus areas
- useful historical context

This separation helps the system answer current questions, historical questions, and identity questions more cleanly.

### 2. Query time pipeline

Each question goes through the following steps:

**Planner**
The planner classifies the question, determines the temporal mode, selects which memory layers to search, and chooses tags that should guide retrieval.

**Retrieval**
The retriever searches the local vector index and re ranks candidates using semantic relevance, layer priority, tag overlap, question type, and temporal relevance.

**Evidence assembly**
The system builds a compact evidence packet from the strongest chunks instead of passing everything through blindly.

**Responder**
The responder writes a grounded answer using only the retrieved evidence. The goal is to keep the answer natural, direct, and useful without inventing anything.

**Verifier**
The verifier checks whether the answer is actually supported by the evidence, whether there are temporal mistakes, and whether the system should accept, soften, or refuse the response.

**Policy layer**
The policy layer standardizes the final response. This matters most for unsupported questions, especially personal preference or belief questions that are not stated anywhere in the data.

### 3. Debug mode

Debug mode is there for observability and testing. It intentionally keeps the full quality pipeline visible.

The UI includes a **Why this answer** drawer that shows:
- planner output
- selected memory layers
- retrieved evidence
- verifier action and confidence
- final policy action
- timing breakdown

That made it much easier to inspect failures and improve behavior during development.

## Response quality choices

The main deep dive decisions were:

### Planner based routing
The system does not treat every question the same way. It first decides whether the question is timeless, current, historical, project focused, or unsupported.

### Freshness aware retrieval
Current questions prioritize current state memory. Historical questions prioritize archive. Identity and project questions prioritize long term memory.

### Verification
The verifier checks groundedness, unsupported claims, and temporal correctness. This is especially useful for questions where a fluent answer can still be wrong.

### Unsupported question handling
If the twin does not have grounded evidence for a personal preference, belief, or favorite, it should not guess. It returns a cautious response instead.

## Evaluation

I built a lightweight evaluation harness to test both normal behavior and failure cases.

### Eval categories

- Identity recall
- Project synthesis
- Current state questions
- Historical questions
- Unsupported questions
- Tone consistency
- Temporal correctness

### Final results

**15 out of 15 passed, 100.0% pass rate**

Category breakdown:

- Identity recall: **3 / 3**
- Project synthesis: **3 / 3**
- Current state: **3 / 3**
- Historical: **2 / 2**
- Unsupported: **2 / 2**
- Tone: **1 / 1**
- Temporal correctness: **1 / 1**

The eval harness checks things like:
- whether an answer exists
- whether sources are present
- whether the final action matches expected behavior
- whether the routed memory layers make sense
- whether required concepts appear
- whether forbidden hallucinated content is avoided

This was useful both for iteration and for making the response quality deep dive concrete.

## Memory lifecycle

The project also includes a simple memory lifecycle.

**Current to archive**
Current state items can expire based on freshness windows.

**Archive to long term**
Archived items can be promoted into long term memory if they look durable and identity relevant.

So the intended flow is:

**current state memory -> archive -> long term memory**

For this take home, that lifecycle is implemented as a lightweight rules based script rather than a fully autonomous memory system.

## Repository structure

```text
digital-twin/
  backend/
  frontend/
  data/
    long_term/
    current/
    archive/
  evals/
  scripts/
  tests/
  README.md
  requirements.txt
  .env.example
````

## How to run the project

### Backend setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your OpenAI API key to `.env`.

### Build the index

```bash
PYTHONPATH=. python scripts/build_index.py
```

### Start the backend

```bash
PYTHONPATH=. uvicorn backend.app:app --reload
```

The backend runs at:

```text
http://127.0.0.1:8000
```

### Start the frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at:

```text
http://127.0.0.1:5173
```

## Run the evals

With the backend running:

```bash
PYTHONPATH=. python evals/run_evals.py
```

This produces:

* a console summary
* detailed per case output
* a saved `eval_results.json`

## Run the memory lifecycle

```bash
PYTHONPATH=. python scripts/run_memory_lifecycle.py
PYTHONPATH=. python scripts/build_index.py
```

This checks for expired current state items, moves them to archive, optionally promotes durable archive items into long term memory, and rebuilds the searchable index.

## Example demo questions

These are the prompts I used most while testing:

* What project best shows your production AI engineering skills?
* Tell me about RepaintWiz
* What are your technical strengths?
* What are you focused on right now?
* What were you working on recently?
* What is your favorite sports team?

## Tradeoffs

A few tradeoffs shaped the implementation.

### Quality over latency

I prioritized routing quality, grounding, verification, and observability over minimal latency. The result is slower than a basic retrieve and answer chatbot, but much easier to trust and debug.

### Verifier always on in debug mode

I kept verification fully enabled in debug mode because debug is meant to show the full quality pipeline, not the fastest path.

### No full external integrations

I did not fully build OAuth or live Google, Slack, or Notion integrations. I chose to spend time on response quality and memory design because that felt like the highest leverage path for this take home.

### Rule based memory lifecycle

Memory consolidation is implemented as a lightweight rules based process rather than a more autonomous production memory system.

## Future work

If I extended this further, I would prioritize:

* Adaptive verification in normal user mode
* Real external integrations and syncing
* Scoped sharing and persona visibility controls
* Richer automated evaluation
* Better evidence compression
* Stronger memory promotion logic
* Streaming responses in the UI

## Why I built it this way

I treated the digital twin problem as more than just RAG with a chat UI.

The hardest part is not writing fluent text. It is making sure the system:

* pulls from the right memory layer
* knows what is current and what is historical
* does not invent unsupported preferences
* can explain why it answered the way it did

That is why I chose **Response Quality** as the deep dive and centered the project around groundedness, temporal awareness, verification, and observability.




