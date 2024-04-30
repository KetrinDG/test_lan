from flask import Flask, request, render_template, jsonify
import spacy
from langdetect import detect
from heapq import nlargest
from stop_words import get_stop_words
import logging
from flask_cors import CORS

# Logger setup
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


app = Flask(__name__)
CORS(app, resources={r"/summarize": {"origins": "*"}})

try:
    # Relative path to the Ukrainian language model
    nlp_uk_path = "uk_core_news_sm/uk_core_news_sm-3.7.0"
    # Load the Ukrainian language model using the relative path
    nlp_uk = spacy.load(nlp_uk_path)

    # Relative path to the English language model
    nlp_en_path = "en_core_web_sm/en_core_web_sm-3.7.1"
    # Load the English language model using the relative path
    nlp_en = spacy.load(nlp_en_path)

except Exception as e:
    logging.error(f"Error loading spaCy models: {e}")
    raise e


# Function to detect the language of the text
def detect_language(text):
    try:
        language = detect(text)
        if language in ["en", "uk"]:
            logging.debug(f"Detected language: {language}")
            return language
        else:
            logging.error("Unknown language")
            return None
    except Exception as e:
        logging.error(f"Error detecting language: {e}")
        return None


# Function to generate text summary
def generate_summary(text, num_sentences_to_select=3):
    language = detect_language(text)
    if language is None:
        return "Error: Unable to detect the language of the text."

    if language == "en":
        nlp = nlp_en
        stop_words = set(get_stop_words("english"))
    elif language == "uk":
        nlp = nlp_uk
        stop_words = set(get_stop_words("ukrainian"))

    # Analyze the text using spaCy
    doc = nlp(text)

    # Count word frequencies
    word_frequencies = {}
    for token in doc:
        if token.text.lower() not in stop_words and token.text not in punctuation:
            word_frequencies[token.text.lower()] = word_frequencies.get(token.text.lower(), 0) + 1

    # Normalize word frequencies
    max_frequency = max(word_frequencies.values(), default=0)
    for word in word_frequencies:
        word_frequencies[word] /= max_frequency

    # Calculate sentence scores
    sentence_scores = {}
    for sent in doc.sents:
        score = sum(word_frequencies.get(word.text.lower(), 0) for word in sent)
        sentence_scores[sent] = score

    # Select sentences with the highest scores
    selected_sentences = nlargest(num_sentences_to_select, sentence_scores, key=sentence_scores.get)

    # Create summary
    summary = ' '.join([sent.text for sent in selected_sentences])
    return summary


# Main route to display the form and process submitted text
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        article = request.form.get("article")
        if not article:
            return "Error: Article is empty. Please provide text for analysis."

        # Generate summary
        summary = generate_summary(article)
        return render_template("result.html", summary=summary)

    return render_template("index.html")


# Route to handle POST requests and generate summary
@app.route("/summarize", methods=["POST"])
def summarize_text():
    data = request.get_json()
    text = data.get("text")

    # Generate summary
    summary = generate_summary(text)

    if summary:
        return jsonify({"summary": summary})
    else:
        logging.error("Failed to generate summary.")
        return jsonify({"error": "Error: Unable to detect the language of the text"}), 400


if __name__ == "__main__":
    app.run()
