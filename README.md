# Search Engine Web App

This is a simple search engine web application built using Flask, JavaScript, and HTML/CSS. It processes search queries, ranks articles based on similarity, and returns relevant results.

## Features
- Search interface with a user-friendly UI
- Flask backend for query processing
- Uses TF-IDF and cosine similarity for ranking
- Handles spelling correction and abbreviation expansion
- Displays ranked search results dynamically
- Supports phrase matching for improved accuracy
- Preprocesses text by removing stopwords and normalizing words

## Technologies Used
- **Backend:** Flask (Python), Pandas, Scikit-learn, SpellChecker
- **Frontend:** HTML, CSS, JavaScript
- **Search Processing:** TF-IDF vectorization, Cosine Similarity
- **Data Storage:** JSON-based dataset

## Preprocessing Steps
1. **Text Cleaning:**
   - Convert text to lowercase
   - Remove special characters and punctuation
2. **Stopword Removal:**
   - Remove common words that do not contribute to meaning
3. **Spell Correction:**
   - Uses a spell checker to correct misspelled words
4. **Abbreviation Expansion:**
   - Expands common abbreviations such as 'AI' to 'Artificial Intelligence'
5. **Vectorization:**
   - Convert processed text into numerical vectors using TF-IDF
6. **Similarity Computation:**
   - Compute similarity scores using Cosine Similarity


