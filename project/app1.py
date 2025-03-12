from flask import Flask, request, jsonify, render_template
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import re
import json
from spellchecker import SpellChecker

# Load data from IRproject.json with explicit UTF-8 encoding
with open("IRproject.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Flatten the JSON into a DataFrame
articles = []
for topic, articles_list in data.items():
    for article in articles_list:
        # Add the topic to each article
        article["topic"] = topic
        articles.append(article)

# Create DataFrame
df = pd.DataFrame(articles)

# Normalize columns
df['total_words_norm'] = df['total_words'] / df['total_words'].max()
df['unique_words_percent_norm'] = df['unique_words_percentage'] / 100
df['stopwords_percent_norm'] = df['stopwords_percentage'] / 100

# Define weights for ranking
weights = {
    'similarity': 0.5,
    'total_words': 0.2,
    'unique_words': 0.2,
    'stopwords': 0.1
}

# Updated stopwords
stopwords = set([
    "a", "an", "the", "and", "or", "in", "of", "to", "for", "with", "is", 
    "on", "at", "as", "by", "this", "that", "it", "if", "from", "but", "are", 
    "was", "were", "be", "been", "has", "have", "had", "do", "does", "did",
    "will", "would", "shall", "should", "can", "could", "may", "might", "must"
])

# Preprocess text
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = [word for word in text.split() if word not in stopwords]
    return ' '.join(tokens)

# Apply preprocessing
df['processed_title'] = df['title'].apply(preprocess_text)
df['processed_content'] = df['content'].apply(preprocess_text)

# Combine title and content for fallback search
df['combined_text'] = df['processed_title'] + " " + df['processed_content']

# Initialize vectorizers
tfidf_vectorizer_title = TfidfVectorizer()
tfidf_matrix_title = tfidf_vectorizer_title.fit_transform(df['processed_title'])

tfidf_vectorizer_content = TfidfVectorizer()
tfidf_matrix_content = tfidf_vectorizer_content.fit_transform(df['combined_text'])

# Spell checker
spell = SpellChecker()
def correct_spelling(query):
    corrected_query = []
    for word in query.split():
        correction = spell.correction(word)
        corrected_query.append(correction if correction is not None else word)
    return " ".join(corrected_query)


# Updated abbreviations
abbreviations = {
    "ai": "artificial intelligence",
    "ml": "machine learning",
    "nn": "neural network",
    "dl": "deep learning",
    "nlg": "natural language generation",
    "nlu": "natural language understanding",
    "cv": "computer vision",
    "nlp": "natural language processing",
    "qml": "quantum machine learning",
    "al": "active learning",
    "cybersec": "cybersecurity",
    "iot": "internet of things",
    "cloudsec": "cloud security",
    "cs": "computer science",
    "ds": "data science",
    "bd": "big data"
}

def expand_abbreviations(query):
    words = query.split()
    return " ".join([abbreviations.get(word, word) for word in words])

# Prioritize phrase matching
def prioritize_phrase_matching(query, df):
    if '"' in query:
        phrases = re.findall(r'"(.*?)"', query)
        for phrase in phrases:
            exact_matches = df[df['processed_title'].str.contains(re.escape(phrase), case=False)]
            if not exact_matches.empty:
                return exact_matches
    return df

def rank_results(scores, df, weights):
    df = df.copy()  # Avoid modifying the original DataFrame
    df['similarity'] = scores
    df['adjusted_score'] = (
        weights['similarity'] * df['similarity'] +
        weights['total_words'] * df['total_words_norm'] +
        weights['unique_words'] * df['unique_words_percent_norm'] +
        weights['stopwords'] * (1 - df['stopwords_percent_norm'])
    )
    # Sort by adjusted score and similarity
    ranked_df = df.sort_values(by=['adjusted_score', 'similarity'], ascending=False)
    return ranked_df
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/search', methods=['POST'])
def search():
    query = request.json.get('query', '').strip()
    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400

    # Preprocess query
    query = expand_abbreviations(query.lower())
    query = correct_spelling(query)

    # Vectorize query for content
    query_vec_content = tfidf_vectorizer_content.transform([query])
    scores_content = cosine_similarity(query_vec_content, tfidf_matrix_content).flatten()

    # Rank content-based results
    top_results_content = rank_results(scores_content, df, weights)

    # Fallback to title if necessary
    if top_results_content.shape[0] < 5 or top_results_content['similarity'].max() < 0.1:
        query_vec_title = tfidf_vectorizer_title.transform([query])
        scores_title = cosine_similarity(query_vec_title, tfidf_matrix_title).flatten()

        # Rank title-based results
        top_results_title = rank_results(scores_title, df, weights)

        # Combine content and title results
        combined_results = pd.concat([top_results_content, top_results_title])
    else:
        combined_results = top_results_content

    # Remove duplicates based on 'link' and keep the top results
    combined_results = combined_results.drop_duplicates(subset=['link'])

    # Ensure we have at least 5 results by padding with lower-ranked ones
    combined_results = combined_results.sort_values(by='adjusted_score', ascending=False).head(5)

    # Ensure required columns exist
    if 'unique_words_percent_norm' not in combined_results.columns:
        combined_results['unique_words_percent_norm'] = 0.0
    if 'stopwords_percent_norm' not in combined_results.columns:
        combined_results['stopwords_percent_norm'] = 0.0

    # Format results
    results = combined_results[['title', 'link', 'total_words', 'unique_words_percent_norm', 'stopwords_percent_norm']].to_dict(orient='records')

    # Return results
    return jsonify(results)




if __name__ == '__main__':
    app.run(debug=True)
