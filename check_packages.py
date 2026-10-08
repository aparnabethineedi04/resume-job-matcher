import sys

packages = ['fastapi', 'uvicorn', 'streamlit', 'sklearn', 'nltk', 'pdfplumber', 'pypdf', 'PyPDF2', 'pytest', 'requests', 'multipart']
for pkg in packages:
    try:
        __import__(pkg)
        print(f"{pkg}: available")
    except ImportError:
        print(f"{pkg}: NOT installed")
