# CareBridge — Healthcare Access & Follow-up Assistant

**An open-source, non-diagnostic prototype** that helps people organize symptoms and prepare a visit summary for a healthcare professional. It does not diagnose, prescribe, or replace a clinician.

> **CareBridge makes the conversation easier to prepare for—not the medical decision.** It turns a person's own notes into a structured visit-preparation summary and presents explicit, limited warning-sign messaging without claiming that a person is safe.

## Team details
- Project lead: Aman Gupta
- Team members: Nishtha Malhotra, Amogh Gupta, Abhiyansh Jain

## College / Incubator information
- Institution: Guru Gobind Singh Indraprastha University,USAR
- Incubator/program: IPU EDC Incubation Centre
- Location: Delhi

## Project title
CareBridge: Healthcare Access and Follow-up Assistant

## Problem statement
People may struggle to organize symptoms, decide what information to share at an appointment, or remember follow-up questions. CareBridge offers a structured intake and a shareable visit-preparation summary. It uses explicit, inspectable rules to flag a small set of emergency warning signs. It is not clinically validated and is not a medical decision-support system.

## Healthcare use case
- Guided symptom and context intake before a future appointment.
- Escalation messaging for selected emergency warning signs.
- Optional context about daily impact, what seems to help or worsen symptoms, and the user's own visit questions.
- Editable, downloadable summary for discussion with a qualified healthcare professional.
- One-click fictional demo example, plus a clear-form action for live judging.
- No account, database, cloud AI service, or external health API. An optional note organizer can use an Ollama model running locally.

**Safety note:** The warning-sign list is incomplete. A result without a flag does not mean a person is safe. When in doubt, contact a healthcare professional; for possible life-threatening emergencies, contact local emergency services.

## Hackathon demo

1. Start the app and explain that the prototype supports visit preparation; it does not diagnose or provide emergency triage.
2. Click **Load sample** to populate clearly fictional information, then submit the form.
3. Review how the summary keeps the user's words, labels missing context as “Not provided,” and can be edited or downloaded.
4. If a local Ollama model is already installed, choose **Organize my notes locally** and explain why its editable draft remains separate from the visit summary. If not, show the optional setup below without entering real information.
5. To demonstrate the limited warning-sign rule, use a clearly simulated selection from the listed options, submit, and explain that it is not a clinical assessment. Click **Clear form** afterward.
6. Run the automated tests to show warning-sign cases, “unsure” behavior, summary generation, and local AI request handling are checked.

Use fictional information throughout the demo. The form is processed by the server running the app. The prototype has no database and does not call cloud AI or health APIs, but a hosted demo still receives submitted data; never enter real patient information.

## Technical stack
- Python 3.10+
- Streamlit web UI
- Transparent rule-based warning-sign checks
- Optional local language model through the Ollama HTTP API (stdlib client; no model bundled)
- Pytest
- Docker

## AI/ML model or framework details
The warning-sign behavior remains a small, deterministic rule set; it is not an ML model and is not clinically validated. An optional, user-triggered note organizer can call a locally running Ollama model (default: `llama3.2:3b`) to organize user-authored narrative into a draft. The prompt prohibits diagnosis, urgency assessment, and treatment recommendations. The model output is explicitly unverified, is kept separate from the visit summary, and is never inserted automatically. No model is downloaded or bundled by CareBridge.

### Optional local AI setup

1. Install Ollama from [ollama.com](https://ollama.com/) on the same machine that runs CareBridge.
2. In a terminal, download a model, for example: `ollama pull llama3.2:3b`.
3. Keep the Ollama service running, launch CareBridge locally, create a visit summary, and choose **Organize my notes locally**.
4. If using another already-installed Ollama model, enter its exact model name in the app.

The app sends only symptom narrative, duration, daily impact, context, and questions to `127.0.0.1:11434`. It does not send name, age, medicines, or warning-sign selections to Ollama. The optional feature is off unless the user presses its button. If Ollama is unavailable or the model is missing, the app reports an error with setup guidance; the ordinary summary still works. The model output may be inaccurate or invent details: review it and do not use it to make care decisions.

**Local means local to the app server.** With a hosted deployment, the notes have already reached the host, and Ollama must run on that host to work. Do not enter real patient information into hosted demos. Standard Docker containers also have their own loopback; this optional feature requires Ollama to be reachable at the configured local address inside the app's network namespace.

## Features
- Responsive intake form with duration, self-described severity, optional daily impact, symptom context, medicines/allergies, and questions for a visit.
- Explicit warning-sign rules with conservative wording; no “all clear” result.
- Optional local-only Ollama note organization, explicitly user-triggered and separate from the summary.
- User-reviewable and editable visit summary with a plain-text download.
- Fictional sample flow and one-click form clearing for repeatable, privacy-aware demos.
- Tests for all listed warning signs, selection combinations, non-reassuring fallback copy, summary fields, the demo-submit-clear UI flow, and local AI request/error behavior.
- Docker support for repeatable local or hosted demos.

## Run locally
Windows PowerShell:
```bash
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Run tests
```bash
pip install -r requirements-dev.txt
pytest
```

## Docker
```bash
docker build -t carebridge .
docker run --rm -p 8501:8501 carebridge
```

## Architecture diagram
- Editable Mermaid source: `docs/architecture.mmd`
- PDF diagram: `docs/architecture.pdf`

## Demo video (mandatory for submission)
- Demo video: https://youtu.be/x2AXKnBO-g8
- Suggested script: `docs/demo_script.md`

## Open-source license
MIT License — see `LICENSE`.

## Presentation (mandatory for submission)
- Slide outline: https://docs.google.com/presentation/d/1Ioe61tB0YoTByGWvJTS-ZtE_5IJvliB8/edit?usp=sharing&ouid=108937792523610505956&rtpof=true&sd=true

## Public repository checklist
- [ ] Team details completed.
- [ ] College/incubator details completed.
- [x] Project title included.
- [x] Problem statement included.
- [x] Healthcare use case included.
- [x] Technical stack included.
- [x] AI/ML/framework details included.
- [ ] 15–20 minute unlisted YouTube demo uploaded and linked.
- [x] Open-source license included.
- [x] Architecture diagram source included.
- [x] Architecture diagram PDF included.
- [ ] Presentation PDF/PPT exported and linked.
- [ ] Repository made public and all links checked.

Do not mark unchecked items complete until you have added real details and verified the uploads.

## Privacy, safety, and limitations
- Use fictional data only; do not enter patient identifiers or real medical records. On a hosted deployment, form entries are processed by the server operator even though this prototype does not intentionally persist them.
- No account, database, cloud AI service, or external health API is included. Optional local Ollama processing is sent to the app host's loopback address only.
- Not for diagnosis, treatment, emergency dispatch, or clinical deployment.
- The warning-sign list is incomplete and not clinically validated.
- Seek professional care for severe, worsening, persistent, or concerning symptoms.
- Review applicable privacy, security, accessibility, and medical-device requirements before deployment.

## Roadmap
1. Clinician review of wording and warning-sign rules.
2. Accessibility and privacy/security review.
3. Formal evaluation plan with approved, de-identified data.
4. Only after appropriate governance: explore a validated model with documented performance and limitations.
