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

import numpy as np
import torch
from mitreattack.stix20 import MitreAttackData
from nltk.tokenize import sent_tokenize
from scipy.spatial.distance import cosine
from transformers import DPRContextEncoder, DPRContextEncoderTokenizer

# Load DPR model and tokenizer
dpr_model = DPRContextEncoder.from_pretrained("facebook/dpr-ctx_encoder-multiset-base")
dpr_tokenizer = DPRContextEncoderTokenizer.from_pretrained("facebook/dpr-ctx_encoder-multiset-base")


def get_document_embedding(document):
    # Sentence tokenization
    sentences = sent_tokenize(document)

    # Tokenize each sentence and obtain embeddings
    embeddings_list = []
    for sentence in sentences:
        input_ids = dpr_tokenizer(sentence, truncation=True, return_tensors="pt")["input_ids"]
        with torch.no_grad():
            embeddings = dpr_model(input_ids).pooler_output
            embeddings_list.append(embeddings.numpy())

    # Calculate the average of embeddings for all sentences
    if embeddings_list:
        document_embedding = np.mean(embeddings_list, axis=0)
        return document_embedding.squeeze()

    return None  # Return None if there are no sentences in the document


def preprocess_text(text):
    text = re.sub(r"[\(\[].*?[\)\]]", "", text)
    text = text.replace("<code>", " ").replace("</code>", " ")  # Replace <code> and </code> with spaces
    return text


def loadmitre(mitre_ids, mitre_docs):
    mitre_attack_data = MitreAttackData("enterprise-attack.json")

    techniques = mitre_attack_data.get_techniques(remove_revoked_deprecated=True)
    print(f"Retrieved {len(techniques)} ATT&CK techniques.")

    for technique in techniques:
        id = technique.external_references[0].external_id
        text = preprocess_text("Attack technique using " + technique.name + ". " + technique.description)
        print(f"Processing {id}")
        mitre_ids.append(id)
        mitre_docs.append(get_document_embedding(text))


def calculate_similarity(doc1, doc2):
    return 1 - cosine(doc1, doc2)


def main():
    mitre_docs = []
    mitre_ids = []
    loadmitre(mitre_ids, mitre_docs)

    cvetext = preprocess_text(
        "Those using Snakeyaml to parse untrusted YAML files may be vulnerable to Denial of Service attacks (DOS). If the parser is running on user supplied input, an attacker may supply content that causes the parser to crash by stack overflow causing an Application Exhaustion Flood. This effect may support a denial of service attack."
    )
    print(cvetext)

    # Get embeddings for each document using DPR
    cvedoc = get_document_embedding(cvetext)

    scoring = {}
    start_time = time.time()

    i = 0
    for mitre_doc in mitre_docs:
        key = mitre_ids[i]
        scoring[key] = np.float64(calculate_similarity(cvedoc, mitre_doc).item())
        i = i + 1

    duration = time.time() - start_time
    print(f"Time={duration}")

    sorted_dict = {key: value for key, value in scoring.items() if isinstance(value, float) and value > 0.49}

    if len(sorted_dict) < 2:
        sorted_dict = dict(sorted(scoring.items(), key=lambda item: item[1], reverse=True)[:2])

    print(json.dumps(sorted_dict))


if __name__ == "__main__":
    main()
