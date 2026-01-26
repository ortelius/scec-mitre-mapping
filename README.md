# SCEC–MITRE Mapping

This repository provides a concise mapping between Software Supply Chain Exploit Chains (SCEC) and the MITRE ATT&CK® framework, helping DevSecOps and platform engineering teams understand how supply chain attacks propagate across CI/CD pipelines and live production systems.

Maintained as part of the Ortelius open-source ecosystem.

## Purpose

MITRE ATT&CK defines adversary behavior but does not explicitly model software supply chain attack paths.

The SCEC model describes attacker movement through:

- Source repositories
- Build systems
- CI/CD workflows
- Artifact registries
- Deployment pipelines
- Runtime environments

This repository maps each SCEC phase to relevant MITRE ATT&CK tactics and techniques to support consistent threat modeling and analysis.

### What’s Included

SCEC → MITRE ATT&CK mappings

### Rationale and references

Machine-readable formats for automation

Example
SCEC Phase	MITRE ATT&CK
Source Compromise	T1195 – Supply Chain Compromise
Build Manipulation	T1554 – Compromise Software Binary
Artifact Poisoning	T1027 – Obfuscated / Tampered Files
Runtime Exploitation	T1059 – Command Execution

## Why It Matters

Most security tooling focuses on pre-deployment detection. Many high-impact incidents occur after deployment, when new vulnerabilities are disclosed and teams lack visibility into what is actually running.

This mapping supports post-deployment vulnerability defense and improved remediation prioritization.

Repository Structure
.
├── mappings/
│   ├── scec-to-mitre.yaml
│   ├── scec-to-mitre.json
│   └── scec-to-mitre.csv
├── docs/
│   └── scec-overview.md
└── README.md

Relationship to Ortelius

- Ortelius focuses on:
- SBOM-to-runtime correlation
- Digital twin modeling of deployed systems
- Detection of newly disclosed vulnerabilities impacting live assets



GitHub “security framework” discoverability

Just tell me.
