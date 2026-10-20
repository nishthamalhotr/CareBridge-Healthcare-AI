import streamlit as st
from carebridge.local_ai import DEFAULT_MODEL, LocalAIError, organize_notes_locally
from carebridge.triage import (
    UNSURE_OPTION,
    URGENT_TERMS,
    assess_intake,
    make_visit_summary,
)

st.set_page_config(
    page_title="CareBridge | Visit preparation",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

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


def clear_generated_content():
    for key in (
        "generated_summary",
        "generated_assessment",
        "summary_preview",
        "local_ai_draft",
        "local_ai_error",
        "intake_narrative",
    ):
        st.session_state.pop(key, None)


def load_fictional_demo():
    st.session_state.update({**FICTIONAL_DEMO, "red_flags": []})
    clear_generated_content()


def clear_form():
    st.session_state.update({**FORM_DEFAULTS, "red_flags": []})
    clear_generated_content()


for key, value in FORM_DEFAULTS.items():
    st.session_state.setdefault(key, value)


# ── Modern UI styling ────────────────────────────────────────────────
st.markdown(
    """
    <style>
    :root {
        --ink: #163b3b;
        --muted: #6b8282;
        --teal: #087f78;
        --teal-dark: #06635e;
        --line: #e1ece8;
    }

    .stApp {
        background:
            radial-gradient(ellipse at 0% 0%, #d9f1e9 0%, transparent 32rem),
            radial-gradient(ellipse at 100% 15%, #e5f5f0 0%, transparent 28rem),
            #f5f9f7;
        color: var(--ink);
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 1320px;
        padding: 2.5rem 2rem 2rem;
    }

    h1, h2, h3, p, label {
        color: var(--ink);
    }

    h2 {
        letter-spacing: -.035em;
        font-weight: 750;
    }

    .brand {
        display: flex;
        align-items: flex-start;
        gap: 1.2rem;
        margin-bottom: 1.7rem;
    }

    .brand-mark {
        display: grid;
        place-items: center;
        flex-shrink: 0;
        width: 4rem;
        height: 4rem;
        border-radius: 1.25rem;
        color: white;
        background: linear-gradient(145deg, #20b3a3, #08736e);
        box-shadow: 0 12px 26px rgba(8, 127, 121, .2);
        font-size: 2rem;
    }

    .brand-kicker {
        color: var(--teal);
        font-size: .76rem;
        font-weight: 800;
        letter-spacing: .13em;
        text-transform: uppercase;
        margin: .1rem 0 .6rem;
    }

    .brand h1 {
        color: var(--ink);
        font-size: clamp(2rem, 3.8vw, 3.2rem);
        font-weight: 800;
        letter-spacing: -.055em;
        line-height: 1.08;
        margin: 0;
    }

    .brand-subtitle {
        color: var(--muted);
        max-width: 650px;
        margin: .8rem 0 0;
        font-size: 1.04rem;
        line-height: 1.7;
    }

    .hero-badges {
        display: flex;
        flex-wrap: wrap;
        gap: .55rem;
        margin-top: 1.15rem;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: .4rem;
        padding: .45rem .8rem;
        border: 1px solid #d8eae4;
        border-radius: 999px;
        color: #17645e;
        background: rgba(255, 255, 255, .8);
        font-size: .77rem;
        font-weight: 700;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #ffffff;
        border: 1px solid var(--line);
        border-radius: 1.15rem;
        box-shadow: 0 8px 30px rgba(27, 71, 63, .055);
    }

    [data-testid="stForm"] {
        padding-top: .6rem;
    }

    [data-testid="stWidgetLabel"] p {
        color: #294b49;
        font-size: .9rem;
        font-weight: 650;
    }

    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        border: 1px solid #dce8e4;
        border-radius: .75rem;
        background: #fbfdfc;
        color: var(--ink);
    }

    [data-testid="stTextInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus {
        border-color: var(--teal);
        box-shadow: 0 0 0 .18rem rgba(8, 127, 121, .12);
    }

    [data-testid="stSelectbox"] > div > div,
    [data-testid="stMultiSelect"] > div > div {
        border-radius: .75rem;
    }

    .stButton button,
    .stDownloadButton button,
    .stFormSubmitButton button {
        min-height: 2.85rem;
        border-radius: .8rem;
        font-weight: 700;
        transition: transform .15s ease, box-shadow .15s ease;
    }

    .stButton button:hover,
    .stDownloadButton button:hover,
    .stFormSubmitButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(22, 59, 59, .1);
    }

    .stFormSubmitButton button,
    .stButton button[kind="primary"] {
        color: white;
        background: linear-gradient(110deg, #0b9387, #08736e);
        border: 0;
        box-shadow: 0 6px 18px rgba(8, 127, 121, .17);
    }

    .stFormSubmitButton button:hover,
    .stButton button[kind="primary"]:hover {
        color: white;
        background: var(--teal-dark);
    }

    [data-testid="stAlert"] {
        border-radius: .9rem;
        border-left-width: 4px;
    }

    .side-heading {
        color: var(--ink);
        font-size: 1.16rem;
        font-weight: 760;
        margin: 0 0 .55rem;
    }

    .side-copy {
        color: var(--muted);
        line-height: 1.75;
        font-size: .92rem;
    }

    .step {
        display: flex;
        gap: .85rem;
        align-items: flex-start;
        padding: 1rem 0;
        border-bottom: 1px solid #edf2f0;
    }

    .step:last-child {
        border-bottom: 0;
        padding-bottom: .15rem;
    }

    .step-number {
        display: grid;
        place-items: center;
        flex: 0 0 2rem;
        height: 2rem;
        border-radius: .7rem;
        color: var(--teal-dark);
        background: #e4f5ef;
        font-size: .85rem;
        font-weight: 800;
    }

    .step strong {
        display: block;
        color: var(--ink);
        font-size: .94rem;
        margin-bottom: .2rem;
    }

    .step span {
        color: var(--muted);
        font-size: .85rem;
        line-height: 1.6;
    }

    [data-testid="stCaptionContainer"] {
        color: var(--muted);
    }

    [data-testid="stExpander"] {
        border: 1px solid var(--line);
        border-radius: .85rem;
        background: #fbfdfc;
    }

    hr {
        border-color: var(--line);
    }

    @media (max-width: 768px) {
        [data-testid="stMainBlockContainer"] {
            padding: 1.25rem .85rem 1.5rem;
        }

        .brand {
            gap: .8rem;
        }

        .brand-mark {
            width: 3rem;
            height: 3rem;
            border-radius: .9rem;
            font-size: 1.5rem;
        }

        .brand h1 {
            font-size: 1.85rem;
        }

        .brand-subtitle {
            font-size: .94rem;
        }

        .hero-badge {
            font-size: .7rem;
        }
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            transition: none !important;
            animation: none !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Header ───────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="brand">
      <div class="brand-mark" aria-hidden="true">✚</div>
      <div>
        <div class="brand-kicker">CAREBRIDGE / VISIT PREPARATION</div>
        <h1>Your health story,<br>clearly organized.</h1>
        <p class="brand-subtitle">
          Prepare for your next healthcare visit with a simple,
          thoughtful summary of what you have been experiencing.
        </p>
        <div class="hero-badges">
          <span class="hero-badge">✓ Your words, your story</span>
          <span class="hero-badge">⌂ Optional local AI</span>
          <span class="hero-badge">♡ Review before sharing</span>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.warning(
    "CareBridge is a visit-preparation tool, not a diagnostic system. "
    "It cannot rule out emergencies. If you may be experiencing a "
    "life-threatening emergency, contact your local emergency services."
)


# ── Demo controls ────────────────────────────────────────────────────
with st.container(border=True):
    demo_description, demo_button, clear_button = st.columns([2.1, 1.1, 0.8])

    with demo_description:
        st.markdown("**Try CareBridge**")
        st.caption(
            "Load fictional sample information to explore the app. "
            "No warning signs are selected in the demo."
        )

    with demo_button:
        st.button(
            "Load sample",
            key="load_demo",
            on_click=load_fictional_demo,
            use_container_width=True,
        )

    with clear_button:
        st.button(
            "Clear form",
            key="clear_form",
            on_click=clear_form,
            use_container_width=True,
        )


form_column, info_column = st.columns([1.8, 1], gap="large")


# ── Intake form ──────────────────────────────────────────────────────
with form_column:
    with st.container(border=True):
        st.subheader("Let's prepare for your visit")
        st.caption(
            "Share only what you are comfortable including. "
            "Optional fields can be left blank."
        )

        with st.form("intake"):
            st.markdown("#### About you")
            name_col, age_col = st.columns([1.4, 1])

            with name_col:
                preferred_name = st.text_input(
                    "Name or initials (optional)",
                    max_chars=60,
                    key="preferred_name",
                    help="Avoid full identifiers.",
                )

            with age_col:
                age = st.selectbox(
                    "Age group",
                    ["Prefer not to say", "Under 18", "18–39", "40–64", "65+"],
                    key="age_band",
                )

            st.markdown("#### Symptoms")
            symptoms = st.text_area(
                "What are you experiencing?",
                placeholder="Describe symptoms in your own words…",
                max_chars=1500,
                height=130,
                key="symptoms",
            )

            duration_col, severity_col = st.columns(2)

            with duration_col:
                duration = st.selectbox(
                    "How long has this been happening?",
                    [
                        "Not specified",
                        "Started today",
                        "1–3 days",
                        "4–7 days",
                        "More than a week",
                    ],
                    key="duration",
                )

            with severity_col:
                severity = st.select_slider(
                    "How severe does it feel?",
                    options=["Mild", "Moderate", "Severe"],
                    key="severity",
                )

            st.markdown("#### Warning signs")
            red_flags = st.multiselect(
                "Are you experiencing any of these?",
                [*URGENT_TERMS, UNSURE_OPTION],
                help=(
                    "This list is incomplete. If you are unsure, feel seriously "
                    "unwell, or symptoms are rapidly worsening, seek professional help."
                ),
                key="red_flags",
            )

            with st.expander("＋ Add more details for your visit"):
                impact = st.text_area(
                    "How has this affected your day?",
                    placeholder="Sleep, work, school, or usual activities.",
                    max_chars=600,
                    key="impact",
                )

                context = st.text_area(
                    "Anything that seems to help or make it worse?",
                    placeholder="Include what you have noticed.",
                    max_chars=600,
                    key="context",
                )

                medications = st.text_area(
                    "Medicines or allergies to mention",
                    placeholder="Optional information for your visit summary.",
                    max_chars=800,
                    height=90,
                    key="medications",
                )

                questions = st.text_area(
                    "What would you like to ask at your visit?",
                    placeholder="Add your questions or concerns.",
                    max_chars=800,
                    key="questions",
                )

            submitted = st.form_submit_button(
                "Create my visit summary",
                type="primary",
                use_container_width=True,
                key="create_summary",
            )


# ── Information panel ────────────────────────────────────────────────
with info_column:
    with st.container(border=True):
        st.markdown(
            '<div class="side-heading">A calmer way to get ready</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="side-copy">A few details can make it easier to '
            'remember what you wanted to discuss with a healthcare professional.</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="step">
              <div class="step-number">1</div>
              <div><strong>Describe</strong>
              <span>Write down your symptoms and when they began.</span></div>
            </div>
            <div class="step">
              <div class="step-number">2</div>
              <div><strong>Review</strong>
              <span>Check the summary and correct anything inaccurate.</span></div>
            </div>
            <div class="step">
              <div class="step-number">3</div>
              <div><strong>Discuss</strong>
              <span>Use your notes to start a conversation with a qualified professional.</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.container(border=True):
        st.markdown(
            '<div class="side-heading">Privacy & demo data</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="side-copy">Use fictional information for demos. '
            'This prototype has no database, but entries are processed by the '
            'server running the app. Optional AI sends narrative notes to Ollama '
            'on the app host. Avoid personal identifiers and sensitive records.</div>',
            unsafe_allow_html=True,
        )

    with st.container(border=True):
        st.markdown(
            '<div class="side-heading">A helpful reminder</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="side-copy">Your notes do not need to be perfect. '
            'Include what you noticed, when it started, and any questions you '
            'want to remember. A clinician can help assess your symptoms.</div>',
            unsafe_allow_html=True,
        )


# ── Generate visit summary ───────────────────────────────────────────
if submitted:
    result = assess_intake(red_flags)

    st.session_state.pop("local_ai_draft", None)
    st.session_state.pop("local_ai_error", None)

    st.session_state["intake_narrative"] = "\n".join(
        f"{label}: {value.strip()}"
        for label, value in (
            ("Symptoms", symptoms),
            ("Duration", duration if duration != "Not specified" else ""),
            ("Daily impact", impact),
            ("What helps or worsens it", context),
            ("Questions or concerns", questions),
        )
        if value.strip()
    )

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


# ── Display summary and optional local AI ────────────────────────────
if st.session_state.get("generated_summary"):
    with form_column:
        with st.container(border=True):
            st.subheader("Your visit-preparation summary")
            st.caption(
                "Review every detail carefully. Edit anything that does not "
                "reflect your experience before downloading or sharing."
            )

            assessment = st.session_state["generated_assessment"]

            if assessment["urgent"]:
                st.error(assessment["message"])
            else:
                st.info(assessment["message"])

            st.text_area(
                "Your editable summary",
                height=320,
                key="summary_preview",
                help="Edit this text before downloading it.",
            )

            st.download_button(
                "Download your visit summary (.txt)",
                data=st.session_state["summary_preview"],
                file_name="carebridge_visit_summary.txt",
                mime="text/plain",
                use_container_width=True,
                type="primary",
            )

        with st.expander("Optional local AI · organize notes on this machine"):
            st.caption(
                "A local Ollama model can help format your narrative into a draft. "
                "Only narrative fields are sent to Ollama on the app host, not your "
                "name, age, medicines, or warning-sign selections. AI can be wrong. "
                "Review the draft carefully. It is not a diagnosis."
            )

            model = st.text_input(
                "Local Ollama model",
                value=DEFAULT_MODEL,
                key="local_ai_model",
                help="For example, llama3.2:3b. Install the model in Ollama first.",
            )

            if st.button(
                "Organize my notes locally",
                key="organize_local_notes",
                use_container_width=True,
            ):
                try:
                    st.session_state["local_ai_draft"] = organize_notes_locally(
                        st.session_state["intake_narrative"],
                        model,
                    )
                    st.session_state.pop("local_ai_error", None)
                except LocalAIError as error:
                    st.session_state["local_ai_error"] = str(error)
                    st.session_state.pop("local_ai_draft", None)

            if st.session_state.get("local_ai_error"):
                st.error(st.session_state["local_ai_error"])

            if st.session_state.get("local_ai_draft"):
                st.text_area(
                    "Unverified AI draft · review before use",
                    value=st.session_state["local_ai_draft"],
                    height=220,
                    key="local_ai_draft_preview",
                )


# ── Footer ───────────────────────────────────────────────────────────
st.divider()
st.caption(
    "CareBridge · Educational prototype · Not a diagnosis or substitute "
    "for professional care · Warning-sign list is incomplete"
)
