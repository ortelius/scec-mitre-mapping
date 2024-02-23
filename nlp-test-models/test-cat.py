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

import nltk
import spacy
from mitreattack.stix20 import MitreAttackData
from nltk.tokenize import sent_tokenize

data = {}

nltk.download("punkt")  # Download the punkt tokenizer


def loadmitre():
    mitre_attack_data = MitreAttackData("enterprise-attack.json")

    techniques = mitre_attack_data.get_techniques(remove_revoked_deprecated=True)
    print(f"Retrieved {len(techniques)} ATT&CK techniques.")

    # Extract and print the desired information
    for technique in techniques:
        id = technique.external_references[0].external_id

        if "." in id:
            continue

        # Sentence tokenization
        # Remove text within square brackets or parentheses
        text = re.sub(r"[\(\[].*?[\)\]]", "", "Attack technique using " + technique.name + ". " + technique.description)
        sentences = sent_tokenize(text)
        data[id] = sentences


def main():

    # Load JSON file containing paragraphs
    loadmitre()

    nlp = spacy.load("en_core_web_lg")

    nlp.add_pipe(
        "classy_classification",
        config={
            "data": data,
            "model": "spacy",
        },
    )

    # Supply paragraph for comparison
    cvetext = "Those using Snakeyaml to parse untrusted YAML files may be vulnerable to Denial of Service attacks (DOS). If the parser is running on user supplied input, an attacker may supply content that causes the parser to crash by stack overflow causing an Application Exhaustion Flood. This effect may support a denial of service attack."
    print(cvetext)
    doc = nlp(cvetext)
    cats = doc._.cats

    sorted_dict = dict(sorted(cats.items(), key=lambda item: item[1], reverse=True))
    print(json.dumps(sorted_dict))


if __name__ == "__main__":
    main()
