import streamlit as st
from carebridge.triage import UNSURE_OPTION, URGENT_TERMS, assess_intake, make_visit_summary

st.set_page_config(page_title="CareBridge | Visit preparation", page_icon="🩺", layout="wide")

FORM_DEFAULTS = {
    "preferred_name": "",
    "age_band": "Prefer not to say",
    "symptoms": "",
    "duration": "Not specified",
    "severity": "Moderate",
    "red_flags": [],
    "medications": "",
    "impact": "",
    "context": "",
    "questions": "",
}

FICTIONAL_DEMO = {
    **FORM_DEFAULTS,
    "preferred_name": "Sample (fictional)",
    "age_band": "18–39",
    "symptoms": "A mild headache started this afternoon after a busy day.",
    "duration": "Started today",
    "severity": "Mild",
    "impact": "A little harder to focus than usual.",
    "context": "No additional details provided.",
    "questions": "What details would be useful to track before a visit?",
}


def _load_fictional_demo() -> None:
    st.session_state.update({**FICTIONAL_DEMO, "red_flags": []})
    st.session_state.pop("generated_summary", None)
    st.session_state.pop("generated_assessment", None)
    st.session_state.pop("summary_preview", None)


def _clear_form() -> None:
    st.session_state.update({**FORM_DEFAULTS, "red_flags": []})
    st.session_state.pop("generated_summary", None)
    st.session_state.pop("generated_assessment", None)
    st.session_state.pop("summary_preview", None)


for key, value in FORM_DEFAULTS.items():
    st.session_state.setdefault(key, value)

st.markdown(
    """
    <style>
    :root {
        --ink: #17343a;
        --muted: #647b80;
        --teal: #087f79;
        --teal-dark: #06645f;
        --line: #dce9e7;
        --surface: #ffffff;
    }
    .stApp {
        background:
            radial-gradient(ellipse at 8% 0%, rgba(186, 231, 224, .42), transparent 32rem),
            #f4f8f7;
        color: var(--ink);
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stMainBlockContainer"] {
        max-width: 1220px;
        padding-top: 2.5rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3, p, label { color: var(--ink); }
    .brand {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin: 0 0 1.6rem;
    }
    .brand-mark {
        display: grid;
        place-items: center;
        width: 3.5rem;
        height: 3.5rem;
        border-radius: 1.15rem;
        color: white;
        background: linear-gradient(145deg, #18a69b, #08736e);
        box-shadow: 0 10px 22px rgba(8, 127, 121, .2);
        font-size: 1.8rem;
    }
    .brand-kicker {
        color: var(--teal);
        font-size: .73rem;
        font-weight: 800;
        letter-spacing: .13em;
        text-transform: uppercase;
        margin-bottom: .2rem;
    }
    .brand h1 {
        font-size: clamp(1.8rem, 3vw, 2.55rem);
        font-weight: 760;
        letter-spacing: -.045em;
        line-height: 1.1;
        margin: 0;
    }
    .brand-subtitle {
        color: var(--muted);
        margin: .35rem 0 0;
        font-size: 1rem;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--surface);
        border-color: var(--line);
        border-radius: 1.15rem;
        box-shadow: 0 12px 32px rgba(32, 74, 74, .055);
    }
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stSelectbox"] > div > div,
    [data-testid="stMultiSelect"] > div > div {
        border-radius: .65rem;
        border-color: #d6e4e2;
        background: #fbfdfd;
    }
    [data-testid="stTextInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus {
        border-color: var(--teal);
        box-shadow: 0 0 0 .15rem rgba(8, 127, 121, .12);
    }
    [data-testid="stFormSubmitButton"] button,
    [data-testid="stDownloadButton"] button {
        min-height: 2.9rem;
        border-radius: .7rem;
        font-weight: 700;
    }
    [data-testid="stFormSubmitButton"] button {
        color: white;
        border: 0;
        background: linear-gradient(100deg, #0a8d83, #08736e);
        box-shadow: 0 7px 16px rgba(8, 127, 121, .17);
    }
    [data-testid="stFormSubmitButton"] button:hover {
        color: white;
        background: var(--teal-dark);
        border: 0;
    }
    .side-heading {
        color: var(--ink);
        font-size: 1.18rem;
        font-weight: 750;
        letter-spacing: -.02em;
        margin: 0 0 .35rem;
    }
    .side-copy { color: var(--muted); line-height: 1.55; }
    .step {
        display: flex;
        gap: .8rem;
        align-items: flex-start;
        padding: .9rem 0;
        border-bottom: 1px solid #edf2f1;
    }
    .step:last-child { border-bottom: 0; padding-bottom: 0; }
    .step-number {
        display: grid;
        place-items: center;
        flex: 0 0 1.8rem;
        height: 1.8rem;
        border-radius: 50%;
        color: var(--teal-dark);
        background: #e5f5f1;
        font-size: .8rem;
        font-weight: 800;
    }
    .step strong { display: block; color: var(--ink); font-size: .92rem; }
    .step span { color: var(--muted); font-size: .84rem; line-height: 1.45; }
    [data-testid="stCaptionContainer"] { color: var(--muted); }
    @media (max-width: 700px) {
        [data-testid="stMainBlockContainer"] { padding: 1.25rem 1rem 2rem; }
        .brand { align-items: flex-start; gap: .75rem; }
        .brand-mark { width: 2.9rem; height: 2.9rem; border-radius: .9rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="brand">
      <div class="brand-mark" aria-hidden="true">✚</div>
      <div>
        <div class="brand-kicker">CareBridge · Visit preparation</div>
        <h1>A little more prepared.<br> A little less overwhelmed.</h1>
        <p class="brand-subtitle">Organize what you’re experiencing and bring a clear summary to your next visit.</p>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.warning(
    "CareBridge does not diagnose or provide medical advice. For a possible life-threatening emergency, "
    "contact your local emergency number now."
)

with st.container(border=True):
    demo_description, demo_button, clear_button = st.columns([2.1, 1.1, 0.8])
    with demo_description:
        st.markdown("**Quick demo**")
        st.caption("Try the form with clearly fictional sample information. Nothing is preselected as a warning sign.")
    with demo_button:
        st.button(
            "Load sample",
            key="load_demo",
            on_click=_load_fictional_demo,
            use_container_width=True,
        )
    with clear_button:
        st.button("Clear form", key="clear_form", on_click=_clear_form, use_container_width=True)

form_column, info_column = st.columns([1.8, 1], gap="large")
with form_column:
    with st.container(border=True):
        st.subheader("Let’s prepare for your visit")
        st.caption("Use your own words. Optional fields can be left blank.")
        with st.form("intake"):
            name, age_band = st.columns([1.4, 1])
            with name:
                preferred_name = st.text_input(
                    "Name or initials (optional; avoid full identifiers)",
                    max_chars=60,
                    key="preferred_name",
                )
            with age_band:
                age = st.selectbox(
                    "Age group",
                    ["Prefer not to say", "Under 18", "18–39", "40–64", "65+"],
                    key="age_band",
                )
            symptoms = st.text_area(
                "What are you experiencing?",
                placeholder="Describe symptoms in your own words…",
                max_chars=1500,
                height=120,
                key="symptoms",
            )
            duration_column, severity_column = st.columns(2)
            with duration_column:
                duration = st.selectbox(
                    "How long has this been happening?",
                    ["Not specified", "Started today", "1–3 days", "4–7 days", "More than a week"],
                    key="duration",
                )
            with severity_column:
                severity = st.select_slider(
                    "How severe does it feel?",
                    options=["Mild", "Moderate", "Severe"],
                    key="severity",
                )
            red_flags = st.multiselect(
                "Any of these warning signs?",
                [*URGENT_TERMS, UNSURE_OPTION],
                help="This list is incomplete. If you are unsure or feel seriously unwell, seek professional help.",
                key="red_flags",
            )
            with st.expander("Add visit details (all optional)"):
                impact = st.text_area(
                    "How has this affected your day?",
                    placeholder="For example: sleep, work, school, or usual activities.",
                    max_chars=600,
                    key="impact",
                )
                context = st.text_area(
                    "Anything that seems to help or make it worse?",
                    placeholder="Include only what you have noticed; it is okay to leave this blank.",
                    max_chars=600,
                    key="context",
                )
                medications = st.text_area(
                    "Medicines or allergies to mention",
                    placeholder="Optional; avoid listing details you do not want included.",
                    max_chars=800,
                    height=90,
                    key="medications",
                )
                questions = st.text_area(
                    "What would you like to ask at your visit?",
                    placeholder="Add your own question or concern.",
                    max_chars=800,
                    key="questions",
                )
            submitted = st.form_submit_button(
                "Create my visit summary",
                type="primary",
                use_container_width=True,
                key="create_summary",
            )

with info_column:
    with st.container(border=True):
        st.markdown('<div class="side-heading">A simple way to get ready</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="side-copy">A few details can make it easier to remember what you wanted to discuss.</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="step"><div class="step-number">1</div><div><strong>Describe</strong><span>Put your symptoms and timing into your own words.</span></div></div>
            <div class="step"><div class="step-number">2</div><div><strong>Review</strong><span>Check the summary and make sure it says what you mean.</span></div></div>
            <div class="step"><div class="step-number">3</div><div><strong>Discuss</strong><span>Use it as a starting point with a qualified professional.</span></div></div>
            """,
            unsafe_allow_html=True,
        )
    with st.container(border=True):
        st.markdown('<div class="side-heading">Privacy & demo data</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="side-copy">Use fictional information for demos. Entries are processed by the server running this app; this prototype has no database and does not call external AI or health APIs. Avoid personal identifiers and sensitive records.</div>',
            unsafe_allow_html=True,
        )

if submitted:
    result = assess_intake(red_flags)
    summary = make_visit_summary(
        name=preferred_name.strip(),
        age_band=age,
        symptoms=symptoms.strip(),
        duration=duration,
        severity=severity,
        red_flags=red_flags,
        medications=medications.strip(),
        result=result,
        impact=impact.strip(),
        context=context.strip(),
        questions=questions.strip(),
    )
    st.session_state["generated_summary"] = summary
    st.session_state["generated_assessment"] = result
    st.session_state["summary_preview"] = summary

if st.session_state.get("generated_summary"):
    with form_column:
        with st.container(border=True):
            st.subheader("Your visit-preparation summary")
            assessment = st.session_state["generated_assessment"]
            if assessment["urgent"]:
                st.error(assessment["message"])
            else:
                st.info(assessment["message"])
            st.text_area("Review or copy your summary", height=300, key="summary_preview")
            st.download_button(
                "Download summary (.txt)",
                data=st.session_state["summary_preview"],
                file_name="carebridge_visit_summary.txt",
                mime="text/plain",
                use_container_width=True,
            )

st.divider()
st.caption("Educational prototype · Not a diagnosis or substitute for professional care · Warning-sign list is incomplete")
