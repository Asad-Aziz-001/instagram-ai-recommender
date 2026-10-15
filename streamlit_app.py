import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:5000")

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Creator Post Recommender",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }

    /* Hide Streamlit default menu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Main container card */
    .main-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 40px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        margin-top: 20px;
    }

    /* Title */
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #a78bfa 0%, #f472b6 50%, #fb923c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }

    .hero-subtitle {
        text-align: center;
        color: rgba(255, 255, 255, 0.6);
        font-size: 1.05rem;
        margin-bottom: 2.5rem;
        font-weight: 400;
    }

    /* Inputs */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 14px !important;
        color: #ffffff !important;
        padding: 14px 18px !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #a78bfa !important;
        box-shadow: 0 0 0 3px rgba(167, 139, 250, 0.2) !important;
        background: rgba(255, 255, 255, 0.12) !important;
    }

    .stTextInput > label {
        color: rgba(255, 255, 255, 0.85) !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
    }

    /* Checkbox */
    .stCheckbox > label {
        color: rgba(255, 255, 255, 0.75) !important;
    }

    /* Button */
    .stButton > button {
        background: linear-gradient(135deg, #a78bfa 0%, #f472b6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 14px 28px !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 24px rgba(167, 139, 250, 0.35) !important;
        margin-top: 10px;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 32px rgba(167, 139, 250, 0.5) !important;
    }

    /* Success message */
    .stAlert {
        background: rgba(167, 139, 250, 0.15) !important;
        border: 1px solid rgba(167, 139, 250, 0.3) !important;
        border-radius: 14px !important;
        color: #ffffff !important;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 18px;
        text-align: center;
    }

    [data-testid="stMetricLabel"] {
        color: rgba(255, 255, 255, 0.6) !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
    }

    /* Headers */
    h2, h3 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* Code block */
    .stCodeBlock {
        background: rgba(0, 0, 0, 0.3) !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
    }

    /* Markdown text */
    .stMarkdown p {
        color: rgba(255, 255, 255, 0.85) !important;
    }

    /* Spinner */
    .stSpinner > div {
        border-top-color: #a78bfa !important;
    }

    /* Divider */
    hr {
        border-color: rgba(255, 255, 255, 0.1) !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------- HERO SECTION ----------
st.markdown('<div class="hero-title">✨ Creator Post Recommender</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">Paste an influencer\'s Instagram URL and get an AI-powered idea for what to post today.</div>',
    unsafe_allow_html=True,
)

# ---------- INPUT FORM ----------
with st.container():
    url = st.text_input(
        "🔗 Inspiration Account URL",
        placeholder="https://www.instagram.com/username/",
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        niche = st.text_input(
            "🎯 Your Niche / Brand (optional)",
            placeholder="e.g. skincare, fitness, food",
        )
    with col2:
        st.write("")
        st.write("")
        mock = st.checkbox("Demo mode", value=False, help="Use sample posts (no scraping)")

# ---------- BUTTON ----------
if st.button("🚀 Get Recommendation", type="primary"):
    if not url.strip():
        st.warning("⚠️ Please enter an Instagram URL.")
    else:
        with st.spinner("🔍 Fetching posts and analyzing..."):
            try:
                r = requests.post(
                    f"{API_URL}/recommend",
                    json={"url": url, "user_niche": niche or None, "mock": mock},
                    timeout=180,
                )
                data = r.json()
            except Exception as e:
                st.error(f"❌ Could not reach API: {e}")
                st.stop()

        if r.status_code != 200:
            st.error(f"❌ {data.get('error', 'Something went wrong')}")
        else:
            a, rec = data["analysis"], data["recommendation"]

            st.success(f"✅ Analyzed {data['posts_analyzed']} recent posts of @{data['username']}")

            st.markdown("---")
            st.subheader("🎯 Post This Today")

            st.markdown(f"**💡 Idea:** {rec['post_idea']}")

            c1, c2 = st.columns(2)
            c1.metric("📱 Format", rec["format"].upper())
            c2.metric("⏰ Best Time", rec["best_time"])

            st.markdown("**✍️ Caption Draft**")
            st.code(rec["caption_draft"], language=None)

            hashtags = " ".join(f"#{h.lstrip('#')}" for h in rec["hashtags"])
            st.markdown(f"**🏷️ Hashtags:** {hashtags}")

            st.info(f"**📊 Why:** {rec['reason']}")

            with st.expander("🔬 Profile Analysis (Evidence)"):
                st.json(a)