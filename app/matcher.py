from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.preprocess import preprocess_text

def calculate_match_score(resume_text: str, job_description_text: str) -> dict:
    """
    Computes TF-IDF vector representations for both texts and calculates
    their Cosine Similarity score on a 0-100 scale.
    
    Returns:
        dict: Contains 'score' (float 0-100), 'resume_terms_count', 'job_terms_count', 'explanation'.
    """
    cleaned_resume = preprocess_text(resume_text)
    cleaned_job = preprocess_text(job_description_text)
    
    # Edge case: If either text is empty after preprocessing
    if not cleaned_resume or not cleaned_job:
        return {
            "score": 0.0,
            "resume_terms_count": 0,
            "job_terms_count": 0,
            "explanation": "Insufficient text content to calculate meaningful similarity."
        }
        
    # Fit TF-IDF on both documents with unigrams and bigrams
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    
    try:
        tfidf_matrix = vectorizer.fit_transform([cleaned_resume, cleaned_job])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        # Convert to percentage score rounded to 2 decimal places
        score = round(float(similarity) * 100, 2)
        
        # Feature names analyzed
        feature_names = vectorizer.get_feature_names()
        
        return {
            "score": score,
            "resume_terms_count": len(cleaned_resume.split()),
            "job_terms_count": len(cleaned_job.split()),
            "vocabulary_size": len(feature_names),
            "explanation": "Cosine similarity computed between TF-IDF term vectors (unigrams + bigrams)."
        }
    except Exception as e:
        return {
            "score": 0.0,
            "resume_terms_count": 0,
            "job_terms_count": 0,
            "explanation": f"Error calculating match: {str(e)}"
        }
