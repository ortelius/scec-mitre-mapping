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

import spacy
from mitreattack.stix20 import MitreAttackData
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Load spaCy model
nlp = spacy.load("en_use_cmlm_lg")


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


def loadmitre(nlp, mitre_docs):
    mitre_attack_data = MitreAttackData("enterprise-attack.json")

    techniques = mitre_attack_data.get_techniques(remove_revoked_deprecated=True)
    print(f"Retrieved {len(techniques)} ATT&CK techniques.")

    # Extract and print the desired information
    for technique in techniques:
        id = technique.external_references[0].external_id

        text = preprocess_text("Attack technique using " + technique.name + ". " + technique.description)
        print(f"Processing {id}")
        mitre_docs[id] = nlp(text)


def calculate_similarity(doc1, doc2):
    similarity = doc1.similarity(doc2)
    return similarity


def main():
    # Load JSON file containing paragraphs
    mitre_docs = {}
    loadmitre(nlp, mitre_docs)

    # Supply paragraph for comparison
    cvetext = preprocess_text(
        "Those using Snakeyaml to parse untrusted YAML files may be vulnerable to Denial of Service attacks (DOS). If the parser is running on user supplied input, an attacker may supply content that causes the parser to crash by stack overflow causing an Application Exhaustion Flood. This effect may support a denial of service attack."
    )
    print(cvetext)
    cvedoc = nlp(cvetext)

    scoring = {}
    # Loop through keys and provide semantic similarity ranking
    for key in mitre_docs:
        try:
            if key is not None and mitre_docs.get(key, None) is not None:
                mitredoc = mitre_docs.get(key, None)
                similarity_score = calculate_similarity(cvedoc, mitredoc)
                scoring[key] = similarity_score
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    sorted_dict = dict(sorted(scoring.items(), key=lambda item: item[1], reverse=True))
    print(json.dumps(sorted_dict))


if __name__ == "__main__":
    main()
