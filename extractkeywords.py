import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

# Updated resources for Python 3.13 / NLTK 3.9+
nltk.download('punkt', quiet=True)     # Still good to keep for legacy
nltk.download('punkt_tab', quiet=True)  # THE FIX: Required for new tokenizers
nltk.download('stopwords', quiet=True)
nltk.download('averaged_perceptron_tagger_eng',
              quiet=True)  # Newer version of tagger


def extract_keywords(text):
    """
    Extracts events, locations, dates, and 'media-hot' keywords.
    Filters out common stop words and punctuation.
    """
    if not text:
        return []

    # 1. Custom 'Hot' words for Otranto Media clients
    # These are high-value terms for celebrities and news outlets
    impact_terms = {
        'love', 'scandal', 'relationship', 'murder', 'wedding',
        'divorce', 'arrest', 'lawsuit', 'breakup', 'rumor', 'exclusive'
    }

    # 2. Tokenize and clean basic text
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text)

    # 3. POS Tagging to find Nouns (Events/Locations) and Adjectives (Sentiments)
    tagged = nltk.pos_tag(tokens)

    keywords = []

    for word, tag in tagged:
        clean_word = word.lower().translate(str.maketrans('', '', string.punctuation))

        if not clean_word or clean_word in stop_words or len(clean_word) < 3:
            continue

        # NNP: Proper Noun (Locations/Events)
        # JJ: Adjective (Descriptive/Scandalous)
        # CD: Cardinal Digit (Dates/Years)
        if tag in ('NNP', 'JJ', 'CD') or clean_word in impact_terms:
            keywords.append(clean_word)

    # 4. Remove duplicates while preserving some order
    unique_keywords = list(dict.fromkeys(keywords))

    return unique_keywords


# --- Example Usage for Otranto Labs ---
if __name__ == "__main__":
    sample_article = """
    A scandalous breakup between celebrity couple John Smith and Jane Scarlett has shocked fans worldwide.
    The couple, who were married for five years, announced their divorce last week amidst rumors of infidelity.
     The news has dominated headlines, with many speculating about the reasons behind the split."""

    found_keywords = extract_keywords(sample_article)
    print(f"Extracted Keywords: {found_keywords}")
