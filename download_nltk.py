import nltk

print("Downloading NLTK resources...")
for resource in ['punkt', 'stopwords', 'wordnet', 'omw-1.4']:
    try:
        nltk.download(resource, quiet=True)
        print(f"Downloaded {resource}")
    except Exception as e:
        print(f"Error downloading {resource}: {e}")
