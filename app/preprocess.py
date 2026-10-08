import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Ensure necessary NLTK data is loaded
try:
    STOP_WORDS = set(stopwords.words("english"))
except LookupError:
    nltk.download("stopwords", quiet=True)
    STOP_WORDS = set(stopwords.words("english"))

try:
    nltk.data.find("corpora/wordnet")
except LookupError:
    nltk.download("wordnet", quiet=True)
    nltk.download("omw-1.4", quiet=True)

lemmatizer = WordNetLemmatizer()

def clean_text(text: str) -> str:
    """
    Cleans raw text by:
    1. Converting to lowercase.
    2. Removing URLs and email addresses.
    3. Replacing special characters and excess whitespace.
    """
    if not text:
        return ""
        
    text = text.lower()
    # Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    # Remove email addresses
    text = re.sub(r"\S+@\S+", " ", text)
    # Replace newlines and tabs with single space
    text = re.sub(r"[\r\n\t]+", " ", text)
    # Keep alphanumeric characters, C++, C#, .NET style terms, and hyphens
    text = re.sub(r"[^\w\s\+\#\.]", " ", text)
    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text

def preprocess_text(text: str) -> str:
    """
    Complete NLP preprocessing pipeline:
    1. Basic text cleaning (lowercasing, punctuation stripping).
    2. Tokenization into individual words.
    3. Removal of standard English stopwords.
    4. Lemmatization of remaining tokens to their root dictionary form.
    5. Re-assembly into a cleaned normalized text string.
    """
    cleaned = clean_text(text)
    if not cleaned:
        return ""
        
    tokens = cleaned.split()
    
    # Filter stopwords and single character non-alphanumeric noise
    filtered_tokens = [
        token for token in tokens 
        if token not in STOP_WORDS and len(token) > 1
    ]
    
    # Lemmatize tokens
    lemmatized_tokens = [
        lemmatizer.lemmatize(token) for token in filtered_tokens
    ]
    
    return " ".join(lemmatized_tokens)

if __name__ == "__main__":
    sample = "Experienced Software Engineer skilled in Developing RESTful APIs with Python and Docker."
    print("--- PREPROCESSING SAMPLE ---")
    print("Original:   ", sample)
    print("Cleaned:    ", clean_text(sample))
    print("Preprocessed:", preprocess_text(sample))
