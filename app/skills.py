import os
import re
import pandas as pd

DEFAULT_SKILLS_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "skills_list.csv")

def load_skills_database(csv_path: str = DEFAULT_SKILLS_CSV) -> list:
    """
    Loads curated skills list from CSV.
    Returns list of dicts: [{'name': 'Python', 'category': 'Languages'}, ...]
    """
    if not os.path.exists(csv_path):
        # Fallback default list if file not found
        return [
            {"name": "Python", "category": "Languages"},
            {"name": "Java", "category": "Languages"},
            {"name": "SQL", "category": "Languages"},
            {"name": "FastAPI", "category": "Frameworks"},
            {"name": "Docker", "category": "DevOps"},
            {"name": "Git", "category": "DevOps"},
            {"name": "Machine Learning", "category": "Concepts"},
        ]
        
    df = pd.read_csv(csv_path)
    return df.to_dict(orient="records")

def extract_skills_from_text(text: str, skills_db: list = None) -> list:
    """
    Extracts known technical skills from text using boundary regex matching.
    """
    if not text:
        return []
        
    if skills_db is None:
        skills_db = load_skills_database()
        
    found_skills = []
    
    # Support both 'skill_name' (from CSV) and 'name' (from fallback dict)
    def get_skill_name(s):
        return s.get("skill_name") or s.get("name", "")

    # Sort skills by length descending so multi-word skills match before single-word substrings
    sorted_skills = sorted(skills_db, key=lambda s: len(get_skill_name(s)), reverse=True)
    
    for skill_item in sorted_skills:
        skill_name = get_skill_name(skill_item)
        if not skill_name:
            continue
        category = skill_item.get("category", "General")
        
        # Escape special characters like C++, C#, .NET
        escaped_skill = re.escape(skill_name)
        
        # Match whole word/phrase with optional plural 's' or 'es'
        pattern = rf"(?i)(?<![a-zA-Z0-9]){escaped_skill}(?:s|es)?(?![a-zA-Z0-9])"
        
        if re.search(pattern, text):
            found_skills.append({
                "skill": skill_name,
                "category": category
            })
            
    # Deduplicate while preserving order
    seen = set()
    unique_skills = []
    for item in found_skills:
        if item["skill"].lower() not in seen:
            seen.add(item["skill"].lower())
            unique_skills.append(item)
            
    return unique_skills

def compare_skills(resume_text: str, job_text: str, skills_db: list = None) -> dict:
    """
    Compares skills in resume vs job description and returns:
    - matched_skills: in both
    - missing_skills: in job description but not in resume
    - extra_skills: in resume but not mentioned in job
    - suggestions: tailored improvement advice
    """
    if skills_db is None:
        skills_db = load_skills_database()
        
    resume_skills = extract_skills_from_text(resume_text, skills_db)
    job_skills = extract_skills_from_text(job_text, skills_db)
    
    resume_skill_names = {s["skill"] for s in resume_skills}
    job_skill_names = {s["skill"] for s in job_skills}
    
    matched = [s for s in job_skills if s["skill"] in resume_skill_names]
    missing = [s for s in job_skills if s["skill"] not in resume_skill_names]
    extra = [s for s in resume_skills if s["skill"] not in job_skill_names]
    
    # Generate action-oriented resume improvement suggestions
    suggestions = []
    if missing:
        missing_names = [s["skill"] for s in missing[:5]]
        suggestions.append(
            f"Add relevant experience or coursework showcasing: {', '.join(missing_names)}."
        )
    if len(matched) == 0 and len(job_skills) > 0:
        suggestions.append(
            "Low skill overlap detected. Review the job requirements and incorporate matching technical keywords."
        )
    elif len(matched) > 0:
        suggestions.append(
            f"Strong alignment on core skills: {', '.join([s['skill'] for s in matched[:4]])}. Ensure these are highlighted in your project bullet points."
        )
        
    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "extra_skills": extra,
        "total_job_skills_count": len(job_skills),
        "total_resume_skills_count": len(resume_skills),
        "suggestions": suggestions
    }
