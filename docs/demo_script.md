# 15–20 minute hackathon demo script

Use fictional example data only. State clearly that this is a visit-preparation prototype, not a diagnostic or emergency-triage system. A hosted demo processes entries on its host server, so never enter real patient information. Make the GitHub repository public, upload the recording as Unlisted on YouTube, and paste the real URL into `README.md`.

- 0:00–2:00 — Give the one-sentence pitch: CareBridge helps people prepare what they want to discuss with a healthcare professional. Explain scope and emergency limitations.
- 2:00–5:00 — Click **Load sample** and show the entirely fictional example. Point out the user's own words, optional context, and no preselected warning signs.
- 5:00–8:00 — Submit and review the generated summary. Edit it, download it, and show how missing details are labeled rather than invented.
- 8:00–11:00 — Select one listed warning sign as an explicitly simulated test, submit, and explain that the deterministic rule only displays escalation copy; it cannot assess a person's condition. Click **Clear form**.
- 11:00–14:00 — Explain the small, inspectable rules and why the prototype deliberately does not use an unvalidated medical model. Show the architecture diagram.
- 14:00–17:00 — Run `pytest` and explain that tests cover every listed warning sign, combinations, the non-reassuring fallback, and summary content.
- 17:00–20:00 — Be candid about limitations, server-side processing in hosted deployments, evaluation still needed, and the governance-first roadmap.
