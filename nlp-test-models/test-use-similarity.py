# Copyright (c) 2021 Linux Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# pylint: disable=E0401,E0611
# pyright: reportMissingImports=false,reportMissingModuleSource=false

import re
from concurrent.futures import ThreadPoolExecutor
from typing import List

import numpy as np
import spacy
import tensorflow_hub as hub
from flask import Flask, jsonify, request
from mitreattack.stix20 import MitreAttackData
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from scipy.spatial.distance import cosine
from spacy.tokens import Doc

app = Flask(__name__)

# Load USE model
use_model_url = "https://tfhub.dev/google/universal-sentence-encoder-large/5"
use_model = hub.load(use_model_url)

# Load spaCy model
nlp = spacy.blank("en")

mitre_docs: List[Doc] = []
mitre_ids: List[str] = []


# Define a function to get the document-level vector
def get_doc_vector(doc):
    embeddings = use_model([doc.text])
    doc_vector = np.array(embeddings[0])
    return np.copy(doc_vector)


# Define a custom spaCy pipeline component for semantic similarity using USE
@spacy.Language.component("use_similarity")
def use_similarity(doc):
    doc.set_extension("use_similarity_vector", getter=get_doc_vector, force=True)
    return doc


# Add the custom component to the spaCy pipeline
nlp.add_pipe("use_similarity")


def preprocess_text(text):

    text = re.sub(r"[\(\[].*?[\)\]]", "", text)
    tokens = word_tokenize(text, preserve_line=True)

    stop_words = set(stopwords.words("english"))
    tokens = [token for token in tokens if token.lower() not in stop_words]

    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]

    return " ".join(tokens)


def loadmitre(nlp, mitre_ids: List[str], mitre_docs: List[Doc]):

    mitre_attack_data = MitreAttackData("enterprise-attack.json")
    techniques = mitre_attack_data.get_techniques(remove_revoked_deprecated=True)
    print(f"Retrieved {len(techniques)} ATT&CK techniques.")

    for technique in techniques:
        id = technique.external_references[0].external_id
        text = preprocess_text("Attack technique using " + technique.name + ". " + technique.description)

        print(f"Processing {id}")
        mitre_docs.append(nlp(text))
        mitre_ids.append(id)


def calculate_similarity(doc1, all_docs):

    with ThreadPoolExecutor() as executor:
        # Use executor.map to parallelize the computation
        similarity_scores = list(executor.map(lambda doc2: 1 - cosine(doc1._.use_similarity_vector, doc2._.use_similarity_vector), all_docs))

    return similarity_scores


# Define the Flask route for the /mitremap endpoint
@app.route("/mitre", methods=["POST"])
def mitremap():
    # Get JSON payload
    data = request.get_json()

    # Extract cvetext from the payload
    cvetext = data.get("cvetext", "")

    # Preprocess the text
    cvetext = preprocess_text(cvetext)

    # Process the text using spaCy
    cvedoc = nlp(cvetext)

    # Loop through keys and provide semantic similarity ranking
    similarity_scores = calculate_similarity(cvedoc, mitre_docs)

    i = 0
    scoring = {}
    for similarity_score in similarity_scores:
        key = mitre_ids[i]
        scoring[key] = similarity_score
        i = i + 1

    # Filter entries with float64 > 0.49
    sorted_dict = {key: value for key, value in scoring.items() if isinstance(value, float) and value > 0.49}

    if len(sorted_dict) < 2:
        sorted_dict = dict(sorted(scoring.items(), key=lambda item: item[1], reverse=True)[:2])

    return jsonify(sorted_dict)


if __name__ == "__main__":
    # Load MITRE data
    loadmitre(nlp, mitre_ids, mitre_docs)

    # Run Flask app
    app.run()
