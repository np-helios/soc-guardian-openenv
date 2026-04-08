---
title: SOC Guardian OpenEnv
emoji: "🛡️"
colorFrom: blue
colorTo: red
sdk: docker
app_port: 7860
pinned: false
---

# SOC Guardian OpenEnv

`soc_guardian_openenv` is an OpenEnv-style benchmark for **early breach detection and SOC response under compute and latency constraints**. The environment is inspired by real-world social-engineering-led intrusions in enterprise hospitality infrastructure, but it is benchmarked through deterministic synthetic scenarios.

## Why this benchmark exists

Security teams do not solve incidents by answering one static question. They process sequential alerts, choose what to investigate, decide which tools to run, decide how much reasoning compute to spend, and determine when to escalate or contain. This benchmark models that workflow as a decision environment.

## Hackathon requirement mapping

- Real-world utility: simulates SOC triage, alert correlation, and incident escalation.
- OpenEnv-style API: `reset()`, `step(action)`, `state()`, and `close()`.
- Three deterministic tasks: `helpdesk_takeover`, `privilege_spiral`, `lateral_breach`.
- Agent graders: each alert has hidden recommended actions, tools, and model tiers used for scoring.
- Reward shaping: rewards early detection, correct containment, and efficient tool/model use while penalizing misses, false positives, cost, and latency.
- Baseline inference: `inference.py` prints the required `[START] / [STEP] / [END]` lines.
- Docker-ready: included `Dockerfile`.
- Demo and docs: FastAPI docs plus an interactive dashboard.

## Tasks

### `helpdesk_takeover`
Easy task. A social-engineering attempt leads into suspicious login and unusual admin page access.

### `privilege_spiral`
Medium task. A compromised identity starts reaching for admin tooling while benign noise alerts compete for attention.

### `lateral_breach`
Hard task. A multi-stage compromise reaches lateral movement with cross-system traffic and a decoy alert mixed in.

## Observation space

Each observation includes:

- currently visible alerts
- system risk level
- attacker progression score
- remaining compute budget
- remaining latency budget
- whether an incident is open
- previous actions
- available tools and model tiers
- scenario-specific analyst notes

Hidden grader targets are kept out of the observation and stored only in internal state.

## Action space

Each action includes:

- response action, such as `investigate`, `request_verification`, `open_incident`, `block_user`, `isolate_host`, or `trigger_incident_response`
- optional target alert id
- selected tool, such as `identity_verifier`, `log_analyzer`, or `network_monitor`
- selected model tier: `cheap`, `balanced`, or `deep`
- optional escalated severity
- optional reasoning note

## Reward logic

The reward combines:

- correct action selection
- correct tool and model choice
- early detection bonus
- breach prevention bonus
- false positive penalty
- false negative penalty
- compute cost penalty
- latency penalty

This gives dense partial signal instead of only success/failure at the end.

## Project files

- `models.py`: typed data models
- `simulator.py`: deterministic SOC environment logic
- `server/app.py`: FastAPI app and interactive UI
- `server/environment.py`: service wrapper
- `client.py`: async HTTP client
- `demo.py`: free-form demo query routing helper
- `inference.py`: baseline runner
- `smoke_test.py`: local sanity checks
- `openenv.yaml`: benchmark metadata
- `Dockerfile`: deployment image

## Local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn server.app:app --reload
```

Open:

- `http://127.0.0.1:8000/` for the dashboard
- `http://127.0.0.1:8000/docs` for the API docs
- `http://127.0.0.1:8000/health` for the health endpoint

## React frontend integration

Your teammate's React frontend has been merged into the project under:

- `frontend/`

It now talks to the live SOC backend instead of only using fake local simulation data.

Run it in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Then open:

- `http://127.0.0.1:8080/`

The Vite dev server proxies `/api/*` calls to the FastAPI backend on `127.0.0.1:8000`.

For production and Hugging Face Docker Spaces, the built React frontend is served directly by the FastAPI container at `/`, and the legacy inline diagnostic dashboard remains available at `/legacy`.

## Smoke test

```bash
python smoke_test.py
```

If the API server is running, the smoke test also verifies `/health` and `/reset`.

## Baseline inference

```bash
python inference.py
```

Environment variables supported:

- `API_BASE_URL`
- `MODEL_NAME`
- `HF_TOKEN`
- `LOCAL_IMAGE_NAME` or `IMAGE_NAME` (reserved for docker-image based execution setups)
- `SOC_GUARDIAN_TASK`

The script uses the OpenAI client for all model calls and emits the required stdout format:

- `[START] task=<task_name> env=<benchmark> model=<model_name>`
- `[STEP] step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>`
- `[END] success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>`

The final printed `score` is clamped to `[0, 1]`.

## Submission validation

The repo includes a local validator script aligned with the hackathon's pre-validation flow:

```bash
chmod +x validate-submission.sh
./validate-submission.sh https://your-space.hf.space .
```

This checks:

- Hugging Face Space `/reset`
- `docker build`
- `openenv validate`

## Notes

This project is OpenEnv-style and hackathon-oriented. If the official validator requires additional metadata fields or exact framework base classes, those can be layered in once the validator version is available locally.
