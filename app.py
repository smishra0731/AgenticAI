import io
from contextlib import redirect_stdout

import streamlit as st

from pipeline import run_research_pipeline

st.set_page_config(page_title="Multi-Agent Research System", page_icon="🔬", layout="wide")

# ---------- Styling ----------
st.markdown(
    """
    <style>
    .block-container { max-width: 1000px; padding-top: 2.5rem; }
    .hero { text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { margin-bottom: 0.2rem; }
    .hero p { opacity: 0.7; margin-top: 0; }
    .steps { display: flex; gap: 10px; margin: 0.5rem 0 1.5rem; flex-wrap: wrap; }
    .step {
        flex: 1; min-width: 190px;
        border: 1px solid rgba(128,128,128,0.3);
        border-radius: 14px; padding: 12px 14px;
        font-size: 0.9rem;
    }
    .step b { display: block; margin-bottom: 2px; }
    .step span { opacity: 0.7; font-size: 0.82rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>🔬 Multi-Agent Research System</h1>
        <p>Enter a topic and let the agents search, read, write and review.</p>
    </div>
    <div class="steps">
        <div class="step"><b>🔎 Step 1 · Search</b><span>Search agent finds recent, reliable information</span></div>
        <div class="step"><b>📖 Step 2 · Read</b><span>Reader agent scrapes the best resource</span></div>
        <div class="step"><b>✍️ Step 3 · Write</b><span>Writer drafts the research report</span></div>
        <div class="step"><b>🧐 Step 4 · Review</b><span>Critic reviews the report</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

STEP_LABELS = {
    "step - 1": "Step 1 of 4: search agent is working…",
    "step - 2": "Step 2 of 4: reader agent is scraping top resources…",
    "step - 3": "Step 3 of 4: writer is drafting the report…",
    "step - 4": "Step 4 of 4: critic is reviewing the report…",
}


class LiveLog(io.StringIO):
    """Captures the print() output of the pipeline and shows it live in the UI."""

    def __init__(self, placeholder, status):
        super().__init__()
        self.placeholder = placeholder
        self.status = status

    def write(self, text):
        super().write(text)
        for key, label in STEP_LABELS.items():
            if key in text:
                self.status.update(label=label, state="running")
        self.placeholder.code(self.getvalue()[-4000:], language=None)
        return len(text)


# ---------- Input ----------
with st.form("research_form"):
    topic = st.text_input("Enter a research topic", placeholder="e.g. Latest advances in solid-state batteries")
    submitted = st.form_submit_button("Run research", type="primary", use_container_width=True)

# ---------- Run the pipeline ----------
if submitted:
    if not topic.strip():
        st.warning("Please enter a research topic.")
    else:
        st.session_state.pop("state", None)
        st.session_state.pop("error", None)
        st.session_state["topic"] = topic.strip()

        with st.status("Starting the research pipeline…", expanded=True) as status:
            log_placeholder = st.empty()
            try:
                with redirect_stdout(LiveLog(log_placeholder, status)):
                    st.session_state["state"] = run_research_pipeline(topic.strip())
                status.update(label="Research complete", state="complete", expanded=False)
            except Exception as e:
                st.session_state["error"] = str(e)
                status.update(label="Something went wrong", state="error")

# ---------- Show results ----------
if st.session_state.get("error"):
    st.error(f"Error: {st.session_state['error']}")

state = st.session_state.get("state")
if state:
    st.subheader(f"Results for: {st.session_state.get('topic', '')}")
    tab_report, tab_feedback, tab_search, tab_scrape = st.tabs(
        ["📄 Final Report", "🧐 Critic Feedback", "🔎 Search Results", "📖 Scraped Content"]
    )
    with tab_report:
        st.markdown(state["report"])
    with tab_feedback:
        st.markdown(state["feedback"])
    with tab_search:
        st.markdown(state["search_results"])
    with tab_scrape:
        st.markdown(state["scraped_content"])