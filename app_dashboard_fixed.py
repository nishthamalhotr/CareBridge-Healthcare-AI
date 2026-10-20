import streamlit as st
from carebridge.local_ai import DEFAULT_MODEL, LocalAIError, organize_notes_locally
from carebridge.triage import (
    UNSURE_OPTION,
    URGENT_TERMS,
    assess_intake,
    make_visit_summary,
)

st.set_page_config(
    page_title="CareBridge | Health Dashboard",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
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

for key, value in FORM_DEFAULTS.items():
    st.session_state.setdefault(key, value)


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


def navigate_to(page_name):
    """Safely change the sidebar page selection before the next rerun."""
    st.session_state["dashboard_page"] = page_name


st.markdown(
    """
    <style>
    :root {
        --ink: #183b3a;
        --muted: #718583;
        --teal: #087f78;
        --teal-dark: #06645f;
        --line: #e4eeeb;
        --surface: #ffffff;
        --canvas: #f4f8f7;
    }
    .stApp {
        background:
          radial-gradient(ellipse at 5% 0%, #e0f4ed 0%, transparent 30rem),
          var(--canvas);
        color: var(--ink);
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stMainBlockContainer"] {
        max-width: 1500px;
        padding: 1.7rem 2rem 2.5rem;
    }
    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: var(--muted);
    }
    h1, h2, h3, h4, p, label { color: var(--ink); }
    h1 { letter-spacing: -.045em; font-weight: 800; }
    h2, h3 { letter-spacing: -.025em; }
    .dash-brand {
        display:flex; align-items:center; gap:.7rem;
        font-size:1.12rem; font-weight:850; color:#173d3a;
        padding:.2rem 0 1.2rem;
    }
    .dash-logo {
        display:grid; place-items:center; width:2.5rem; height:2.5rem;
        border-radius:.85rem; color:white;
        background:linear-gradient(145deg,#25b7a5,#08736e);
        box-shadow:0 8px 20px #087f782b; font-size:1.35rem;
    }
    .eyebrow {
        text-transform:uppercase; letter-spacing:.14em; font-size:.72rem;
        color:#0a8279; font-weight:850; margin-bottom:.35rem;
    }
    .muted { color:var(--muted); }
    .hero {
        padding:1.55rem 1.7rem; border:1px solid #dcece6;
        border-radius:1.35rem;
        background:linear-gradient(115deg,#ffffff 0%,#f0faf6 100%);
        box-shadow:0 10px 35px #214e4310;
        margin-bottom:1.2rem;
    }
    .hero p { color:#6b817e; margin-bottom:.1rem; }
    .hero-tag {
        display:inline-block; padding:.42rem .7rem; border-radius:999px;
        border:1px solid #d9ebe4; background:white; color:#216c63;
        font-size:.76rem; font-weight:750; margin:.6rem .3rem 0 0;
    }
    .metric-card {
        border:1px solid var(--line); border-radius:1.05rem;
        background:white; padding:1.05rem 1.15rem;
        min-height:125px; box-shadow:0 5px 20px #193e3610;
    }
    .metric-label { color:#758985; font-size:.79rem; font-weight:700; }
    .metric-value { color:#173d3a; font-size:1.7rem; font-weight:850; margin:.28rem 0; }
    .metric-foot { color:#81918e; font-size:.77rem; }
    .panel-title { font-size:1.08rem; font-weight:800; margin-bottom:.15rem; }
    .panel-subtitle { color:var(--muted); font-size:.87rem; margin-bottom:.7rem; }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background:#fff; border:1px solid var(--line);
        border-radius:1.1rem; box-shadow:0 7px 26px #193e3609;
    }
    [data-testid="stWidgetLabel"] p { color:#294b49; font-size:.9rem; font-weight:650; }
    [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
        border:1px solid #dce8e4; border-radius:.72rem; background:#fbfdfc;
    }
    [data-testid="stSelectbox"] > div > div, [data-testid="stMultiSelect"] > div > div {
        border-radius:.72rem;
    }
    .stButton button, .stDownloadButton button, .stFormSubmitButton button {
        min-height:2.65rem; border-radius:.75rem; font-weight:750;
    }
    .stFormSubmitButton button, .stButton button[kind="primary"] {
        background:linear-gradient(110deg,#0b9387,#08736e); color:white; border:0;
    }
    [data-testid="stAlert"] { border-radius:.85rem; }
    .side-nav-label {
        color:#81928f; font-size:.7rem; font-weight:850;
        text-transform:uppercase; letter-spacing:.12em; margin:.7rem 0 .3rem;
    }
    .sidebar-note {
        border-radius:.85rem; padding:.9rem; background:#f0f8f5;
        border:1px solid #dfede7; font-size:.83rem; color:#56716c;
        line-height:1.6;
    }
    div[data-testid="stProgress"] > div > div { background:#0b9387; }
    hr { border-color:var(--line); }
    @media(max-width:768px) {
        [data-testid="stMainBlockContainer"] { padding:1rem .8rem 1.5rem; }
        .hero { padding:1.15rem; }
        .metric-value { font-size:1.35rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar navigation / actions
with st.sidebar:
    st.markdown(
        '<div class="dash-brand"><div class="dash-logo">✚</div><div>CareBridge</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="side-nav-label">Workspace</div>', unsafe_allow_html=True)
    page = st.radio(
        "Dashboard sections",
        ["Overview", "Prepare a visit", "My summary", "Privacy & help"],
        label_visibility="collapsed",
        key="dashboard_page",
    )
    st.divider()
    st.markdown('<div class="side-nav-label">Quick actions</div>', unsafe_allow_html=True)
    st.button("Load fictional demo", on_click=load_fictional_demo, use_container_width=True)
    st.button("Clear intake", on_click=clear_form, use_container_width=True)
    st.markdown(
        '<div class="sidebar-note"><b>Not for emergencies</b><br>'
        'CareBridge organizes notes for a healthcare visit. It does not diagnose or '
        'rule out emergencies. Contact local emergency services for a life-threatening emergency.</div>',
        unsafe_allow_html=True,
    )
    st.caption("Educational prototype · No patient database")

summary_exists = bool(st.session_state.get("generated_summary"))
assessment = st.session_state.get("generated_assessment", {})
intake_started = bool(st.session_state.get("symptoms", "").strip())
severity = st.session_state.get("severity", "Moderate")
red_flags = st.session_state.get("red_flags", [])

st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">HEALTHCARE WORKSPACE</div>
      <h1 style="margin:.1rem 0 .4rem;">Your health visit dashboard</h1>
      <p>Organize symptoms, prepare questions, and build a clear summary to review with a clinician.</p>
      <span class="hero-tag">✦ Visit preparation</span>
      <span class="hero-tag">⌂ Optional local AI</span>
      <span class="hero-tag">♡ Review before sharing</span>
    </div>
    """,
    unsafe_allow_html=True,
)

if page == "Overview":
    # Dashboard overview cards
    c1, c2, c3, c4 = st.columns(4)
    cards = [
        ("INTAKE STATUS", "Ready to start" if not intake_started else "In progress",
         "Enter symptoms to begin"),
        ("VISIT SUMMARY", "Created" if summary_exists else "Not created",
         "Editable and downloadable" if summary_exists else "Generate from your intake"),
        ("SEVERITY", severity, "Your selected description"),
        ("WARNING SIGNS", str(len(red_flags)), "Selected items · not a diagnosis"),
    ]
    for col, (label, value, foot) in zip((c1, c2, c3, c4), cards):
        with col:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">{label}</div>'
                f'<div class="metric-value">{value}</div><div class="metric-foot">{foot}</div></div>',
                unsafe_allow_html=True,
            )

    st.write("")
    left, right = st.columns([1.55, 1], gap="large")
    with left:
        with st.container(border=True):
            st.markdown('<div class="panel-title">Your visit workspace</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="panel-subtitle">A simple workflow to get ready for a healthcare appointment.</div>',
                unsafe_allow_html=True,
            )
            step_cols = st.columns(3)
            for col, number, title, detail in [
                (step_cols[0], "01", "Describe", "Add symptoms and timing."),
                (step_cols[1], "02", "Review", "Check warning signs and details."),
                (step_cols[2], "03", "Prepare", "Edit and download your summary."),
            ]:
                with col:
                    st.markdown(
                        f'<div style="background:#f0f8f5;border-radius:.8rem;padding:.9rem;min-height:145px;">'
                        f'<div style="color:#0a8279;font-weight:850;font-size:.78rem;">STEP {number}</div>'
                        f'<div style="font-weight:800;margin:.4rem 0;">{title}</div>'
                        f'<div style="font-size:.83rem;color:#718583;">{detail}</div></div>',
                        unsafe_allow_html=True,
                    )
            st.write("")
            st.button(
                "Start preparing my visit →",
                type="primary",
                use_container_width=True,
                on_click=navigate_to,
                args=("Prepare a visit",),
            )
    with right:
        with st.container(border=True):
            st.markdown('<div class="panel-title">Current session</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="panel-subtitle">This prototype keeps the current intake in Streamlit session state.</div>',
                unsafe_allow_html=True,
            )
            st.progress(1.0 if summary_exists else (0.35 if intake_started else 0.0))
            st.caption("Preparation progress")
            if summary_exists:
                st.success("Your summary is ready to review.")
                if assessment.get("urgent"):
                    st.error(assessment.get("message", "Please seek appropriate medical help."))
                else:
                    st.info(assessment.get("message", "Review your summary before sharing."))
            elif intake_started:
                st.info("Your intake has started. Finish the form and create your summary.")
            else:
                st.caption("No intake entered yet. You can load fictional sample data to explore.")
            st.divider()
            st.markdown("**Helpful reminder**")
            st.caption("Include when symptoms began, how they affect daily life, and questions you want to remember.")

    with st.container(border=True):
        st.markdown('<div class="panel-title">Quick start</div>', unsafe_allow_html=True)
        st.write("Use the navigation on the left to enter symptoms or open an existing summary.")
        q1, q2 = st.columns(2)
        with q1:
            st.button(
                "Open visit intake",
                use_container_width=True,
                on_click=navigate_to,
                args=("Prepare a visit",),
            )
        with q2:
            st.button(
                "View my summary",
                use_container_width=True,
                disabled=not summary_exists,
                on_click=navigate_to,
                args=("My summary",),
            )

elif page == "Prepare a visit":
    st.markdown("## Prepare a visit")
    st.caption("Share only what you are comfortable including. Optional fields can be left blank.")
    form_column, info_column = st.columns([1.65, 1], gap="large")

    with form_column:
        with st.container(border=True):
            st.markdown("### About you")
            with st.form("intake"):
                name_col, age_col = st.columns([1.4, 1])
                with name_col:
                    preferred_name = st.text_input("Name or initials (optional)", max_chars=60, key="preferred_name",
                                                   help="Avoid full identifiers.")
                with age_col:
                    age = st.selectbox("Age group", ["Prefer not to say", "Under 18", "18–39", "40–64", "65+"],
                                       key="age_band")

                st.markdown("### Symptoms")
                symptoms = st.text_area("What are you experiencing?",
                                        placeholder="Describe symptoms in your own words…",
                                        max_chars=1500, height=125, key="symptoms")
                duration_col, severity_col = st.columns(2)
                with duration_col:
                    duration = st.selectbox("How long has this been happening?",
                                            ["Not specified", "Started today", "1–3 days", "4–7 days",
                                             "More than a week"], key="duration")
                with severity_col:
                    severity = st.select_slider("How severe does it feel?",
                                                options=["Mild", "Moderate", "Severe"], key="severity")

                st.markdown("### Warning signs")
                red_flags = st.multiselect(
                    "Are you experiencing any of these?",
                    [*URGENT_TERMS, UNSURE_OPTION],
                    help="This list is incomplete. If you are unsure, feel seriously unwell, or symptoms are rapidly worsening, seek professional help.",
                    key="red_flags",
                )
                with st.expander("＋ Add more details for your visit"):
                    impact = st.text_area("How has this affected your day?",
                                          placeholder="Sleep, work, school, or usual activities.",
                                          max_chars=600, key="impact")
                    context = st.text_area("Anything that seems to help or make it worse?",
                                           placeholder="Include what you have noticed.",
                                           max_chars=600, key="context")
                    medications = st.text_area("Medicines or allergies to mention",
                                               placeholder="Optional information for your visit summary.",
                                               max_chars=800, height=85, key="medications")
                    questions = st.text_area("What would you like to ask at your visit?",
                                             placeholder="Add your questions or concerns.",
                                             max_chars=800, key="questions")
                submitted = st.form_submit_button("Create my visit summary", type="primary", use_container_width=True)

    with info_column:
        with st.container(border=True):
            st.markdown("### Your checklist")
            for n, title, detail in [
                ("1", "Describe symptoms", "Include what you feel and when it started."),
                ("2", "Select warning signs", "If unsure or seriously unwell, seek professional advice."),
                ("3", "Add useful context", "Mention impact, medicines, allergies, and questions."),
                ("4", "Review before sharing", "Correct details that do not reflect your experience."),
            ]:
                st.markdown(
                    f'<div style="display:flex;gap:.75rem;padding:.7rem 0;border-bottom:1px solid #edf2f0;">'
                    f'<div style="min-width:2rem;height:2rem;display:grid;place-items:center;'
                    f'background:#e4f5ef;color:#08736e;border-radius:.65rem;font-weight:850;">{n}</div>'
                    f'<div><b>{title}</b><div style="color:#718583;font-size:.84rem;margin-top:.2rem;">{detail}</div></div></div>',
                    unsafe_allow_html=True,
                )
        with st.container(border=True):
            st.markdown("### Privacy note")
            st.caption("This prototype has no database, but entries are processed by the server running the app. Avoid personal identifiers and sensitive records.")

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
            name=preferred_name.strip(), age_band=age, symptoms=symptoms.strip(),
            duration=duration, severity=severity, red_flags=red_flags,
            medications=medications.strip(), result=result, impact=impact.strip(),
            context=context.strip(), questions=questions.strip(),
        )
        st.session_state["generated_summary"] = summary
        st.session_state["generated_assessment"] = result
        st.session_state["summary_preview"] = summary
        st.success("Summary created. Open **My summary** in the sidebar to review it.")

elif page == "My summary":
    st.markdown("## My visit summary")
    st.caption("Review the summary carefully and edit anything that is inaccurate before downloading.")
    if not st.session_state.get("generated_summary"):
        with st.container(border=True):
            st.info("No summary yet. Complete the intake first.")
            st.button(
                "Go to visit intake →",
                type="primary",
                on_click=navigate_to,
                args=("Prepare a visit",),
            )
    else:
        assessment = st.session_state["generated_assessment"]
        if assessment.get("urgent"):
            st.error(assessment.get("message", "Please seek appropriate medical help."))
        else:
            st.info(assessment.get("message", "Review your summary before sharing."))
        with st.container(border=True):
            st.text_area("Editable summary", height=340, key="summary_preview",
                         help="Edit this text before downloading it.")
            st.download_button(
                "Download visit summary (.txt)",
                data=st.session_state["summary_preview"],
                file_name="carebridge_visit_summary.txt",
                mime="text/plain",
                type="primary",
                use_container_width=True,
            )
        with st.expander("Optional local AI · organize narrative notes"):
            st.caption("Ollama runs on the app host. Only narrative notes are sent, not name, age, medicines, or warning-sign selections. AI can be wrong; review its output.")
            model = st.text_input("Local Ollama model", value=DEFAULT_MODEL, key="local_ai_model")
            if st.button("Organize my notes locally", use_container_width=True):
                try:
                    st.session_state["local_ai_draft"] = organize_notes_locally(
                        st.session_state["intake_narrative"], model
                    )
                    st.session_state.pop("local_ai_error", None)
                except LocalAIError as error:
                    st.session_state["local_ai_error"] = str(error)
                    st.session_state.pop("local_ai_draft", None)
            if st.session_state.get("local_ai_error"):
                st.error(st.session_state["local_ai_error"])
            if st.session_state.get("local_ai_draft"):
                st.text_area("Unverified AI draft · review before use",
                             value=st.session_state["local_ai_draft"], height=220,
                             key="local_ai_draft_preview")

elif page == "Privacy & help":
    st.markdown("## Privacy & help")
    st.caption("Important information about how to use this educational prototype.")
    p1, p2 = st.columns(2, gap="large")
    with p1:
        with st.container(border=True):
            st.markdown("### Data handling")
            st.write("- There is no database in this prototype.")
            st.write("- Intake is processed by the server running the app.")
            st.write("- Avoid full identifiers and sensitive records.")
            st.write("- Optional AI sends narrative notes to Ollama on the app host.")
    with p2:
        with st.container(border=True):
            st.markdown("### Safe use")
            st.write("- CareBridge is not a diagnostic system.")
            st.write("- The warning-sign list is incomplete.")
            st.write("- It cannot rule out emergencies.")
            st.write("- Seek professional advice for concerning or worsening symptoms.")
    st.warning("If you may be experiencing a life-threatening emergency, contact your local emergency services.")

st.divider()
st.caption("CareBridge · Healthcare visit-preparation dashboard · Educational prototype · Not a diagnosis or substitute for professional care.")
