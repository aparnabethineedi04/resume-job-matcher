import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.extractor import extract_text, extract_text_from_pdf
from app.preprocess import clean_text, preprocess_text
from app.matcher import calculate_match_score
from app.skills import extract_skills_from_text, compare_skills, load_skills_database

client = TestClient(app)

# -------------------------------------------------------------
# 1. Extraction Tests
# -------------------------------------------------------------
def test_extractor_plain_text():
    """Verify string extraction handles standard text inputs."""
    text = "  Senior Python Developer with 5 years experience.  "
    extracted = extract_text(text)
    assert extracted == "Senior Python Developer with 5 years experience."

def test_extractor_empty_string_error():
    """Verify empty string throws ValueError."""
    with pytest.raises(ValueError, match="Input text is empty."):
        extract_text("   ")

def test_extractor_empty_pdf_error():
    """Verify 0-byte PDF stream throws ValueError."""
    with pytest.raises(ValueError, match="Provided PDF file is empty"):
        extract_text_from_pdf(b"")

# -------------------------------------------------------------
# 2. Preprocessing Tests
# -------------------------------------------------------------
def test_preprocess_cleaning():
    """Verify URLs, emails, and excess punctuation are cleaned."""
    raw = "Contact me at dev@example.com or visit https://github.com/mydev for Python & Docker!"
    cleaned = clean_text(raw)
    assert "dev@example.com" not in cleaned
    assert "https" not in cleaned
    assert "python" in cleaned
    assert "docker" in cleaned

def test_preprocess_lemmatization_and_stopwords():
    """Verify stopwords are removed and words are lemmatized."""
    text = "The engineer is developing scalable applications using Python"
    preprocessed = preprocess_text(text)
    # 'is', 'the', 'using' are stopwords
    assert "is" not in preprocessed.split()
    assert "the" not in preprocessed.split()
    assert "python" in preprocessed
    assert "develop" in preprocessed or "developing" in preprocessed

# -------------------------------------------------------------
# 3. Matching Tests (Scoring Edge Cases)
# -------------------------------------------------------------
def test_matcher_identical_texts():
    """Identical texts must produce a 100% similarity score."""
    text = "Python developer skilled in FastAPI, Docker, and PostgreSQL databases."
    res = calculate_match_score(text, text)
    assert res["score"] == 100.0

def test_matcher_unrelated_texts():
    """Completely unrelated text should yield very low similarity (< 10%)."""
    resume = "Python software engineer building RESTful APIs with FastAPI and Docker."
    job = "Sous chef needed with 5 years experience in french baking, pastry, and kitchen sanitation."
    res = calculate_match_score(resume, job)
    assert res["score"] < 10.0

def test_matcher_empty_input_edge_case():
    """Empty or whitespace-only inputs should return score 0.0 safely without crashing."""
    res = calculate_match_score("", "Valid job description requiring Python")
    assert res["score"] == 0.0
    assert res["resume_terms_count"] == 0

# -------------------------------------------------------------
# 4. Skills Extraction & Comparison Tests
# -------------------------------------------------------------
def test_skills_extraction_multi_word():
    """Verify multi-word and single-word skills are correctly identified."""
    sample_text = "Proficient in Python, Machine Learning, Docker, and REST APIs."
    skills = extract_skills_from_text(sample_text)
    skill_names = {s["skill"] for s in skills}
    assert "Python" in skill_names
    assert "Machine Learning" in skill_names
    assert "Docker" in skill_names
    assert "REST API" in skill_names or "REST APIs" in skill_names

def test_skills_comparison_matched_and_missing():
    """Verify accurate separation of matched vs missing skills."""
    resume = "Experienced in Python and Docker."
    job = "Looking for an engineer skilled in Python, Docker, Kubernetes, and AWS."
    
    comp = compare_skills(resume, job)
    matched_names = {s["skill"] for s in comp["matched_skills"]}
    missing_names = {s["skill"] for s in comp["missing_skills"]}
    
    assert "Python" in matched_names
    assert "Docker" in matched_names
    assert "Kubernetes" in missing_names
    assert "AWS" in missing_names
    assert len(comp["suggestions"]) > 0

# -------------------------------------------------------------
# 5. API Integration Tests
# -------------------------------------------------------------
def test_api_analyze_endpoint_success():
    """Test POST /analyze endpoint with valid payload returns 200 and expected schema."""
    payload = {
        "resume_text": "Python Backend Developer with experience in FastAPI, PostgreSQL, and Git.",
        "job_description": "Hiring Python Engineer with FastAPI, PostgreSQL, and Docker skills."
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "match_score" in data
    assert data["match_score"] > 10.0
    assert any(s["skill"] == "FastAPI" for s in data["matched_skills"])
    assert any(s["skill"] == "Docker" for s in data["missing_skills"])

def test_api_validation_error_short_input():
    """Test POST /analyze rejects input shorter than 10 characters with 422 Unprocessable Entity."""
    response = client.post("/analyze", json={"resume_text": "Short", "job_description": "Python dev"})
    assert response.status_code == 422
