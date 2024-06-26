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
import os
import re
import sys

import joblib
import stanza
import uvicorn
from fastapi import FastAPI, Response
from mitreattack.stix20 import MitreAttackData
from pydantic import BaseModel  # pylint: disable=E0611
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Define a set of POS tags corresponding to stop words (adjust as needed)
stop_words = {
    "ADP",  # adposition 'to'
    "AUX",  # auxiliary 'is'
    "CCONJ",  # coordinating conjunction 'and'
    "DET",  # determiner 'the'
    "INTJ",  # interjection 'oh'
    "PART",  # particle 'to'
    "PRON",  # pronoun 'it'
    "PUNCT",  # punctuation '.'
    "SCONJ",  # subordinating conjunction 'if'
    "SYM",  # symbol '$'
    "X",  # other 'etc.'
}

# Use a set for faster membership checking
stop_words_set = set(stop_words)

stanza.download("en")  # Download English model for Stanza
nlp = stanza.Pipeline(lang="en", processors="tokenize,mwt,pos,lemma,depparse")
vectorizer = TfidfVectorizer()
mitre_data = []  # type: ignore

# Init FastAPI
app = FastAPI(
    title=__name__,
    description="RestAPI endpoint for retrieving Mitre Techiques",
    version="10.0.0",
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    servers=[{"url": "http://localhost:8080", "description": "Local Server"}],
    contact={
        "name": "Ortelius Open Source Project",
        "url": "https://github.com/ortelius/ortelius/issues",
        "email": "support@ortelius.io",
    },
    debug=True,
)


class CveText(BaseModel):
    cvetext: str


def preprocess(text):
    text = text.replace("<code>", " ").replace("</code>", " ")
    text = text.replace("XSS", "Cross-Site Scripting")
    text = text.replace("DOS", "Denial of Service")
    return re.sub(r"\(Citation: [^)]+\)", "", text)


def process_document(doc):
    tokens = []

    for sent in doc.sentences:
        for word in sent.words:
            if word.pos not in stop_words_set:
                tokens.append(word.lemma)

    return " ".join(tokens)


def calculate_capitalized_words_weight(doc):
    weight = []
    for sent in doc.sentences:
        for word in sent.words:
            if word.text[0].isupper() and word.pos not in stop_words_set:
                weight.append(word.text)
    return " ".join(weight)


def calculate_similarity(doc1, doc2, vectorizer):
    processed_doc1, words_weight1 = doc1
    processed_doc2, words_weight2 = doc2

    weighted_doc1 = processed_doc1.lower() + " " + words_weight1.lower()
    weighted_doc2 = processed_doc2.lower() + " " + words_weight2.lower()

    tfidf_matrix = vectorizer.fit_transform([weighted_doc1, weighted_doc2])
    text_similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

    combined_similarity = text_similarity_matrix[0][1]

    return combined_similarity


def load_mitre(nlp, mitre_data_file):
    mitre_data = []

    if os.path.exists(mitre_data_file):
        # Load mitre_data from the file if it exists
        with open(mitre_data_file, "rb") as file:
            mitre_data = joblib.load(file)
    else:
        # Calculate mitre_data if the file doesn't exist
        for mitre_json in ["enterprise-attack.json", "mobile-attack.json", "ics-attack.json"]:
            mitre_attack_data = MitreAttackData(mitre_json)

            techniques = mitre_attack_data.get_techniques(remove_revoked_deprecated=True)
            print(f"Retrieved {len(techniques)} ATT&CK techniques from {mitre_json}")

            for i, technique in enumerate(techniques):
                id = technique.external_references[0].external_id

                text = f"Attack technique using {technique.name}. {technique.description}"
                print(f"Processing {id}")

                doc = nlp(preprocess(text))
                processed_doc = process_document(doc)
                capitalized_words_weight = calculate_capitalized_words_weight(doc)

                mitre_data.append((id, processed_doc, capitalized_words_weight))

        # Save mitre_data to the file
        with open(mitre_data_file, "wb") as file:
            joblib.dump(mitre_data, file)

    return mitre_data


# Define the Flask route for the /mitre endpoint
@app.post("/msapi/mitre")
def mitremap(data: CveText):

    # Extract cvetext from the payload
    cvetext = data.cvetext
    cvedoc = nlp(preprocess(cvetext))
    cvedoc_processed = process_document(cvedoc)
    cvedoc_words_weight = calculate_capitalized_words_weight(cvedoc)

    scoring = {}

    for id, mitre_processed, mitre_words_weight in mitre_data:
        similarity_score = calculate_similarity((cvedoc_processed, cvedoc_words_weight), (mitre_processed, mitre_words_weight), vectorizer)
        scoring[id] = similarity_score

    # Filter entries with float64 > 0.25
    sorted_dict = {key: value for key, value in scoring.items() if isinstance(value, float) and value > 0.25}

    if len(sorted_dict) < 2:
        sorted_dict = dict(sorted(scoring.items(), key=lambda item: item[1], reverse=True)[:2])

    sorted_dict = dict(sorted(sorted_dict.items(), key=lambda item: item[1], reverse=True))
    json_str = json.dumps(sorted_dict, indent=4, default=str)
    return Response(content=json_str, media_type="application/json")


loaddata = False
if "--loaddata" in sys.argv:
    loaddata = True

mitre_data_file = "mitre.joblib"
mitre_data = load_mitre(nlp, mitre_data_file)

if __name__ == "__main__":
    # Check if --loaddata flag is provided
    if not loaddata:
        uvicorn.run(app, port=8080)
