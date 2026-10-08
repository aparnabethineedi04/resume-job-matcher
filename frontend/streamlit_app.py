import streamlit as st
import requests
import os
import sys

# Add parent directory to path for standalone execution fallback
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.extractor import extract_text_from_pdf
from app.matcher import calculate_match_score
from app.skills import compare_skills, load_skills_database

st.set_page_config(
    page_title="Resume Analyzer & Job Matcher",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    .main-title {
        font-size: 32px;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 5px;
    }
    .sub-title {
        font-size: 16px;
        color: #4B5563;
        margin-bottom: 25px;
    }
    .badge-matched {
        background-color: #D1FAE5;
        color: #065F46;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 600;
        display: inline-block;
        margin: 3px;
    }
    .badge-missing {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 600;
        display: inline-block;
        margin: 3px;
    }
    .badge-extra {
        background-color: #E0E7FF;
        color: #3730A3;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 600;
        display: inline-block;
        margin: 3px;
    }
    .score-card {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# ----------------------------------------------------
# SIDEBAR
# ----------------------------------------------------
st.sidebar.markdown("### ⚙️ Engine Settings")
execution_mode = st.sidebar.radio(
    "Processing Mode",
    ["FastAPI Backend (REST API)", "Direct Local Engine (In-Memory)"],
    help="Select whether to send requests to the FastAPI microservice or process directly."
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔒 Privacy Notice")
st.sidebar.info(
    "Zero File Retention: Resumes are parsed in volatile RAM and immediately discarded. No personal data or documents are ever saved to disk."
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 About")
st.sidebar.caption(
    "Built with FastAPI, Streamlit, Scikit-Learn (TF-IDF + Cosine Similarity), and NLTK."
)

# ----------------------------------------------------
# MAIN CONTENT
# ----------------------------------------------------
st.markdown('<div class="main-title">📄 Resume Analyzer & Job Matcher</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">NLP-Powered Resume Scoring, Skill Gap Analysis & Custom Recommendations</div>',
    unsafe_allow_html=True
)

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("1. Candidate Resume")
    input_method = st.radio("Input Format", ["Upload PDF Resume", "Paste Plain Text"], horizontal=True)
    
    resume_text = ""
    uploaded_pdf_bytes = None
    
    if input_method == "Upload PDF Resume":
        uploaded_file = st.file_uploader("Upload resume PDF", type=["pdf"], help="Select a standard text-based PDF resume.")
        if uploaded_file:
            uploaded_pdf_bytes = uploaded_file.read()
            try:
                resume_text = extract_text_from_pdf(uploaded_pdf_bytes)
                st.success(f"✅ Successfully extracted {len(resume_text.split())} words from **{uploaded_file.name}**.")
            except Exception as e:
                st.error(f"❌ Extraction Error: {e}")
    else:
        sample_resume_default = """Experienced Python Software Engineer with 3+ years in developing scalable RESTful APIs using FastAPI and Flask. Proficient in Docker, PostgreSQL, Redis, and Git. Strong background in Machine Learning, Pandas, and Unit Testing."""
        resume_text = st.text_area(
            "Paste resume text here:",
            value=sample_resume_default,
            height=240
        )

with col_right:
    st.subheader("2. Target Job Description")
    sample_job_default = """We are seeking a Backend Engineer skilled in Python, FastAPI, and Docker. Experience with PostgreSQL, Redis, Kubernetes, AWS, and CI/CD pipelines is strongly required. Must have experience building REST APIs and writing automated unit tests."""
    job_description = st.text_area(
        "Paste target job description here:",
        value=sample_job_default,
        height=280
    )

st.markdown("---")

if st.button("🚀 Analyze Resume & Match Job", use_container_width=True, type="primary"):
    if not resume_text.strip():
        st.warning("⚠️ Please provide candidate resume text or upload a valid PDF.")
    elif not job_description.strip():
        st.warning("⚠️ Please enter a job description to compare against.")
    else:
        with st.spinner("Analyzing semantics, computing TF-IDF similarity, and matching skills..."):
            result_data = None
            
            if execution_mode == "FastAPI Backend (REST API)":
                try:
                    res = requests.post(
                        f"{API_URL}/analyze",
                        json={"resume_text": resume_text, "job_description": job_description},
                        timeout=5
                    )
                    if res.status_code == 200:
                        result_data = res.json()
                    else:
                        st.warning(f"FastAPI returned error {res.status_code}. Falling back to internal engine.")
                except Exception as ex:
                    st.info("FastAPI service not reached at localhost:8000. Running via embedded direct engine.")
            
            # Fallback to direct local engine if API mode is offline
            if result_data is None:
                skills_db = load_skills_database()
                match_res = calculate_match_score(resume_text, job_description)
                skills_res = compare_skills(resume_text, job_description, skills_db)
                result_data = {
                    "match_score": match_res["score"],
                    "matched_skills": skills_res["matched_skills"],
                    "missing_skills": skills_res["missing_skills"],
                    "extra_skills": skills_res["extra_skills"],
                    "suggestions": skills_res["suggestions"],
                    "metadata": {
                        "resume_words": match_res["resume_terms_count"],
                        "job_words": match_res["job_terms_count"]
                    }
                }
                
            # ----------------------------------------------------
            # DISPLAY RESULTS
            # ----------------------------------------------------
            st.markdown("## 📊 Analysis Results")
            
            score = result_data["match_score"]
            matched_skills = result_data["matched_skills"]
            missing_skills = result_data["missing_skills"]
            extra_skills = result_data["extra_skills"]
            suggestions = result_data["suggestions"]
            
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Overall Match Score", f"{score}%")
            with m2:
                st.metric("Matched Skills", len(matched_skills))
            with m3:
                st.metric("Missing Skills", len(missing_skills))
            with m4:
                st.metric("Extra Resume Skills", len(extra_skills))
                
            # Score progress bar
            score_color = "green" if score >= 70 else ("orange" if score >= 40 else "red")
            st.progress(min(int(score), 100))
            
            if score >= 70:
                st.success("🌟 **High Match:** Excellent semantic alignment with target role requirements.")
            elif score >= 40:
                st.info("⚖️ **Moderate Match:** Core foundation is present, but several key skills are missing.")
            else:
                st.error("⚠️ **Low Match:** Low keyword and terminology overlap. Significant tailoring recommended.")
                
            st.markdown("---")
            
            # Skills breakdown columns
            c_match, c_miss, c_extra = st.columns(3)
            
            with c_match:
                st.markdown("### ✅ Matched Skills")
                if matched_skills:
                    for item in matched_skills:
                        st.markdown(f'<span class="badge-matched">{item["skill"]} ({item["category"]})</span>', unsafe_allow_html=True)
                else:
                    st.write("No direct technical skills matched.")
                    
            with c_miss:
                st.markdown("### ⚠️ Missing Required Skills")
                if missing_skills:
                    for item in missing_skills:
                        st.markdown(f'<span class="badge-missing">{item["skill"]} ({item["category"]})</span>', unsafe_allow_html=True)
                else:
                    st.write("🎉 No missing skills found from target job description!")
                    
            with c_extra:
                st.markdown("### ℹ️ Additional Candidate Skills")
                if extra_skills:
                    for item in extra_skills:
                        st.markdown(f'<span class="badge-extra">{item["skill"]} ({item["category"]})</span>', unsafe_allow_html=True)
                else:
                    st.write("No additional distinct skills detected.")
                    
            st.markdown("---")
            
            # Suggestions
            st.subheader("💡 Tailored Resume Recommendations")
            if suggestions:
                for idx, sugg in enumerate(suggestions, 1):
                    st.markdown(f"**{idx}.** {sugg}")
            else:
                st.write("Your resume is well-aligned with the target job requirements.")
