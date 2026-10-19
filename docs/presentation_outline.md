# CareBridge — Presentation Outline

Export these slides to PDF/PPT and add the final file link to `README.md`.

## Slide 1 — Title
CareBridge: Healthcare Access and Follow-up Assistant
Team: [names] | Institution: [college/incubator]

## Slide 2 — Problem
- People may have difficulty organizing symptoms and preparing for appointments.
- The prototype focuses on preparation and clear limitations, not diagnosis.

## Slide 3 — Proposed solution
- Guided intake with optional context, transparent warning-sign rules, editable visit summary, user-controlled download.
- Repeatable demo with fictional sample input; no account, database, external AI service, or external health API.

## Slide 4 — Healthcare use case
- People preparing for a non-emergency appointment.
- Not for emergency triage, diagnosis, treatment, or clinical deployment.

## Slide 5 — Demo flow
1. Load the explicitly fictional sample.
2. Review duration, self-described severity, and optional context.
3. Generate, edit, and download the visit-preparation summary.
4. Demonstrate a simulated warning-sign selection, explain the limits, then clear the form.

## Slide 6 — Architecture
Show `architecture.pdf` or render `architecture.mmd`.

## Slide 7 — Technical stack
Python, Streamlit, deterministic rules, Pytest, Docker.

## Slide 8 — AI/ML approach
Current version intentionally has no ML model. Future ML requires governance, approved data, validation, bias assessment, privacy/security review, and clinician oversight.

## Slide 9 — Evaluation and limitations
Automated tests cover all currently listed warning signs, selections in combination, conservative fallback wording, and summary fields. The app is not clinically validated; usability, accessibility, false-negative risk, privacy, and equity need further evaluation. Hosted deployments process entries on their server.

## Slide 10 — Roadmap
Expert review, accessibility/security review, formal evaluation plan, and only then consideration of validated models.
