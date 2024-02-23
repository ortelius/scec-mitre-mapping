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

import json
import re
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import spacy
import tensorflow_hub as hub
from mitreattack.stix20 import MitreAttackData
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from numba import jit

# Load USE model

use_model_url = "https://tfhub.dev/google/universal-sentence-encoder-large/5"
use_model = hub.load(use_model_url)

# Load spaCy model
nlp = spacy.blank("en")  # spacy.load("en_core_web_lg")


# Define a function to get the document-level vector
def get_doc_vector(doc):
    # Get embeddings for the entire document text
    embeddings = use_model([doc.text])

    # Combine embeddings to get a document-level representation
    doc_vector = np.array(embeddings[0])

    # Return a new copy of the vector to ensure a new memory address for each document
    return np.copy(doc_vector)


# Define a custom spaCy pipeline component for semantic similarity using USE
@spacy.Language.component("use_similarity")
def use_similarity(doc):

    # Add the document-level vector to the doc as an extension
    doc.set_extension("use_similarity_vector", getter=get_doc_vector, force=True)
    return doc


# Add the custom component to the spaCy pipeline
nlp.add_pipe("use_similarity")


@jit(nopython=True)
def cosine_similarity(vector1, vector2):
    dot_product = np.dot(vector1, vector2)
    norm1 = np.linalg.norm(vector1)
    norm2 = np.linalg.norm(vector2)
    similarity = np.float64(dot_product / (norm1 * norm2))
    return similarity


def preprocess_text(text):

    text = re.sub(r"[\(\[].*?[\)\]]", "", text)

    # Tokenization
    tokens = word_tokenize(text, preserve_line=True)

    # Remove stop words
    stop_words = set(stopwords.words("english"))
    tokens = [token for token in tokens if token.lower() not in stop_words]

    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]

    # Join the processed tokens back into a string
    processed_text = " ".join(tokens)

    return processed_text


def loadmitre(nlp, mitre_ids, mitre_docs):
    mitre_attack_data = MitreAttackData("enterprise-attack.json")

    techniques = mitre_attack_data.get_techniques(remove_revoked_deprecated=True)
    print(f"Retrieved {len(techniques)} ATT&CK techniques.")

    # Extract and print the desired information
    for technique in techniques:
        id = technique.external_references[0].external_id

        text = preprocess_text("Attack technique using " + technique.name + ". " + technique.description)
        print(f"Processing {id}")
        mitre_docs.append(nlp(text))
        mitre_ids.append(id)


def calculate_similarity(doc1, all_docs):

    with ThreadPoolExecutor() as executor:
        # Use executor.map to parallelize the computation
        similarity_scores = list(executor.map(lambda doc2: cosine_similarity(doc1._.use_similarity_vector, doc2._.use_similarity_vector), all_docs))

    return similarity_scores


def main():
    # Load JSON file containing paragraphs
    mitre_docs = []
    mitre_ids = []
    loadmitre(nlp, mitre_ids, mitre_docs)

    # Supply paragraph for comparison
    cvetext = preprocess_text(
        "Those using Snakeyaml to parse untrusted YAML files may be vulnerable to Denial of Service attacks (DOS). If the parser is running on user supplied input, an attacker may supply content that causes the parser to crash by stack overflow causing an Application Exhaustion Flood. This effect may support a denial of service attack."
    )
    print(cvetext)
    cvedoc = nlp(cvetext)

    scoring = {}
    # Loop through keys and provide semantic similarity ranking

    start_time = time.time()
    similarity_scores = calculate_similarity(cvedoc, mitre_docs)
    duration = time.time() - start_time
    print(f"Time={duration}")

    i = 0
    for similarity_score in similarity_scores:
        key = mitre_ids[i]
        scoring[key] = similarity_score
        i = i + 1

    # Filter entries with float64 > 0.49
    sorted_dict = {key: value for key, value in scoring.items() if isinstance(value, float) and value > 0.49}

    if len(sorted_dict) < 2:
        sorted_dict = dict(sorted(scoring.items(), key=lambda item: item[1], reverse=True)[:2])

    print(json.dumps(sorted_dict))


if __name__ == "__main__":
    main()
