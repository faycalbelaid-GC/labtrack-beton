import streamlit as st

st.set_page_config(
    page_title="LabTrack — Suivi d'essais béton",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.stApp {
    background: #060a0f;
    background-image:
        radial-gradient(ellipse at 20% 20%, #0a2a1a18 0%, transparent 60%),
        radial-gradient(ellipse at 80% 80%, #0a1a2a18 0%, transparent 60%);
}

section[data-testid="stSidebar"] {
    background: #080d12 !important;
    border-right: 1px solid #1a2a1a;
}

.lab-header {
    background: linear-gradient(135deg, #0a1f0a 0%, #060d1a 100%);
    border: 1px solid #1a3a1a;
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.lab-header::after {
    content: 'LAB';
    position: absolute;
    right: 24px;
    top: 50%;
    transform: translateY(-50%);
    font-family: 'Space Mono', monospace;
    font-size: 5rem;
    font-weight: 700;
    color: #1a3a1a;
    letter-spacing: 0.3em;
    pointer-events: none;
}
.lab-header h1 {
    font-family: 'Space Mono', monospace;
    font-size: 1.8rem;
    color: #4ade80;
    margin: 0;
    letter-spacing: -0.02em;
}
.lab-header p {
    color: #4a6a4a;
    margin: 6px 0 0 0;
    font-size: 0.85rem;
    font-family: 'Space Mono', monospace;
}

.stat-card {
    background: #0a1208;
    border: 1px solid #1a3a1a;
    border-radius: 12px;
    padding: 20px 24px;
    position: relative;
    overflow: hidden;
}
.stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #4ade80, #22d3ee);
}
.stat-card .stat-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: #4a6a4a;
    text-transform: uppercase;
    letter-spacing: 0.15em;
}
.stat-card .stat-value {
    font-family: 'Space Mono', monospace;
    font-size: 2.2rem;
    font-weight: 700;
    color: #4ade80;
    line-height: 1.2;
}
.stat-card .stat-sub {
    font-size: 0.75rem;
    color: #4a6a4a;
}

.section-tag {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: #4ade80;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    border-left: 2px solid #4ade80;
    padding-left: 10px;
    margin-bottom: 16px;
    display: block;
}

.essai-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 4px;
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    font-weight: 700;
}
.badge-compression { background: #1a3a1a; color: #4ade80; border: 1px solid #4ade80; }
.badge-flexion     { background: #1a2a3a; color: #22d3ee; border: 1px solid #22d3ee; }
.badge-traction    { background: #3a2a1a; color: #fb923c; border: 1px solid #fb923c; }

/* Inputs */
.stTextInput input, .stNumberInput input, .stSelectbox select, .stTextArea textarea {
    background: #0a1208 !important;
    border: 1px solid #1a3a1a !important;
    color: #e2e8f0 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.85rem !important;
    border-radius: 8px !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: #4ade80 !important;
    box-shadow: 0 0 0 2px #4ade8022 !important;
}

/* Buttons */
.stButton button {
    background: linear-gradient(135deg, #166534, #14532d) !important;
    color: #4ade80 !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    border: 1px solid #4ade8044 !important;
    border-radius: 8px !important;
    padding: 10px 24px !important;
    width: 100%;
    letter-spacing: 0.05em;
    transition: all 0.2s;
}
.stButton button:hover { opacity: 0.85; }

.stDownloadButton button {
    background: linear-gradient(135deg, #1e3a5f, #1d4ed8) !important;
    color: #93c5fd !important;
    font-family: 'Space Mono', monospace !important;
    border: 1px solid #3b82f644 !important;
    border-radius: 8px !important;
    width: 100%;
}

/* Tabs */
div[data-testid="stTabs"] button {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.8rem !important;
    color: #4a6a4a;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #4ade80 !important;
    border-bottom-color: #4ade80 !important;
}

/* Dataframe */
[data-testid="stDataFrame"] { border: 1px solid #1a3a1a; border-radius: 8px; }

/* Sidebar labels */
.stSelectbox label, .stNumberInput label, .stTextInput label, .stSlider label {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.75rem !important;
    color: #4a6a4a !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* Metric */
[data-testid="stMetricValue"] {
    font-family: 'Space Mono', monospace !important;
    color: #4ade80 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Header
st.markdown("""
<div class="lab-header">
    <h1>🧪 LabTrack</h1>
    <p>Dashboard de suivi d'essais béton · Compression · Flexion · Traction</p>
</div>
""", unsafe_allow_html=True)

# ── Navigation tabs
tab1, tab2, tab3 = st.tabs([
    "📋  Saisie des essais",
    "📊  Tableaux de bord",
    "📈  Analyses statistiques",
])

from pages import saisie, dashboard, statistiques

with tab1:
    saisie.render()

with tab2:
    dashboard.render()

with tab3:
    statistiques.render()
