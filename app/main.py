from fastapi import FastAPI, HTTPException, UploadFile, File, Form, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from app.extractor import extract_text_from_pdf, extract_text
from app.matcher import calculate_match_score
from app.skills import compare_skills, load_skills_database

# Initialize FastAPI application
app = FastAPI(
    title="Resume Analyzer & Job Matcher API",
    description="NLP-powered API for parsing resumes, calculating job match scores, and extracting skills.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load skills database at startup
SKILLS_DB = load_skills_database()

# Pydantic Request Models
class AnalyzeRequest(BaseModel):
    resume_text: str = Field(..., min_length=10, description="Plain text content of candidate resume")
    job_description: str = Field(..., min_length=10, description="Job description text")

class SkillItem(BaseModel):
    skill: str
    category: str

class AnalyzeResponse(BaseModel):
    match_score: float
    matched_skills: List[SkillItem]
    missing_skills: List[SkillItem]
    extra_skills: List[SkillItem]
    suggestions: List[str]
    metadata: Dict[str, Any]

@app.get("/")
def read_root():
    """Health check and welcome endpoint."""
    return {
        "status": "online",
        "message": "Welcome to Resume Analyzer & Job Matcher API",
        "docs_url": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    """Liveness probe."""
    return {"status": "healthy"}

@app.get("/skills")
def list_supported_skills():
    """Returns the list of all indexed technical skills."""
    return {
        "total_skills": len(SKILLS_DB),
        "skills": SKILLS_DB
    }

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_text(request: AnalyzeRequest):
    """
    Analyzes resume and job description text strings:
    - Calculates TF-IDF cosine similarity match score (0-100%).
    - Extracts and compares technical skills.
    - Generates actionable resume suggestions.
    """
    resume = request.resume_text.strip()
    job = request.job_description.strip()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume text cannot be empty."
        )
    if not job:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job description text cannot be empty."
        )
        
    # Matcher score
    match_result = calculate_match_score(resume, job)
    
    # Skill comparison
    skills_result = compare_skills(resume, job, SKILLS_DB)
    
    return AnalyzeResponse(
        match_score=match_result["score"],
        matched_skills=skills_result["matched_skills"],
        missing_skills=skills_result["missing_skills"],
        extra_skills=skills_result["extra_skills"],
        suggestions=skills_result["suggestions"],
        metadata={
            "resume_words": match_result["resume_terms_count"],
            "job_words": match_result["job_terms_count"],
            "total_job_skills": skills_result["total_job_skills_count"],
            "total_resume_skills": skills_result["total_resume_skills_count"],
            "explanation": match_result["explanation"]
        }
    )

@app.post("/analyze-file", response_model=AnalyzeResponse)
async def analyze_file(
    job_description: str = Form(..., min_length=10),
    resume_file: UploadFile = File(...)
):
    """
    Accepts a PDF resume upload + job description text.
    Extracts text in-memory (zero file persistence for privacy) and runs full analysis.
    """
    if not resume_file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported for upload."
        )
        
    pdf_bytes = await resume_file.read()
    
    try:
        extracted_resume_text = extract_text_from_pdf(pdf_bytes)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
        
    match_result = calculate_match_score(extracted_resume_text, job_description)
    skills_result = compare_skills(extracted_resume_text, job_description, SKILLS_DB)
    
    return AnalyzeResponse(
        match_score=match_result["score"],
        matched_skills=skills_result["matched_skills"],
        missing_skills=skills_result["missing_skills"],
        extra_skills=skills_result["extra_skills"],
        suggestions=skills_result["suggestions"],
        metadata={
            "filename": resume_file.filename,
            "resume_words": match_result["resume_terms_count"],
            "job_words": match_result["job_terms_count"],
            "total_job_skills": skills_result["total_job_skills_count"],
            "total_resume_skills": skills_result["total_resume_skills_count"]
        }
    )
