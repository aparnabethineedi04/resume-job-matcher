from app.matcher import calculate_match_score
from app.skills import compare_skills, load_skills_database

skills_db = load_skills_database()

# Pair 1: High Match
resume_1 = """
Senior Python Backend Developer with 4+ years of experience developing high-performance RESTful APIs
using FastAPI, Flask, and PostgreSQL. Proficient in Docker, Git, CI/CD, Redis, and unit testing.
Experienced with Microservices architecture, Machine Learning pipelines, and Linux server management.
"""
job_1 = """
We are looking for a Senior Backend Software Engineer.
Requirements:
- Strong proficiency in Python and FastAPI or Flask.
- Experience with PostgreSQL, Redis, and building scalable REST APIs.
- Hands-on experience with Docker, CI/CD, and Microservices.
- Solid understanding of Data Structures and automated testing.
"""

# Pair 2: Moderate Match
resume_2 = """
Frontend Web Developer with 3 years experience building responsive user interfaces using React, JavaScript,
TypeScript, HTML, CSS, and Tailwind CSS. Familiar with Git, REST APIs, and Node.js.
"""
job_2 = """
Full-Stack Python Engineer:
Requirements:
- 3+ years experience with Python, Django or FastAPI backend development.
- Strong SQL and PostgreSQL database design.
- Docker, AWS, and Cloud deployment.
- Frontend knowledge of React and JavaScript is a plus.
"""

# Pair 3: Low Match
resume_3 = """
Creative Digital Marketing Specialist with 5 years experience in SEO, social media marketing, content creation,
Google Ads, brand management, and customer engagement analytics.
"""
job_3 = """
Cloud DevOps Engineer:
Requirements:
- Hands-on expertise with Kubernetes, Docker, Terraform, and AWS cloud infrastructure.
- CI/CD automation using Jenkins and GitHub Actions.
- Linux systems administration and Python or Bash scripting.
"""

print("=== REAL BENCHMARK RESULTS ON 3 SAMPLE PAIRS ===")
for i, (res, jb, title) in enumerate([(resume_1, job_1, "High Match (Backend Python Dev)"), (resume_2, job_2, "Moderate Match (Frontend React Dev to Full-Stack)"), (resume_3, job_3, "Low Match (Marketing Specialist to DevOps)")], 1):
    m = calculate_match_score(res, jb)
    s = compare_skills(res, jb, skills_db)
    matched = [item['skill'] for item in s['matched_skills']]
    missing = [item['skill'] for item in s['missing_skills']]
    print(f"\nPair {i}: {title}")
    print(f"Match Score: {m['score']}%")
    print(f"Matched Skills ({len(matched)}): {', '.join(matched) if matched else 'None'}")
    print(f"Missing Skills ({len(missing)}): {', '.join(missing) if missing else 'None'}")
