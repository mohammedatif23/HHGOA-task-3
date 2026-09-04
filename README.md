# HH GOA TASK 3 - Face Identification & Evidence Integrity

## Overview

This project implements a face identification and evidence verification
pipeline using reverse image search, face recognition, evidence hashing,
and blockchain-based integrity verification.

The system takes a reference face image, searches for visually similar
online results, identifies potential social-media candidates, downloads
candidate images when available, compares faces, and generates a
verifiable evidence report.

The generated evidence is protected using SHA-256 hashing and a
blockchain-based integrity mechanism.

---

## Problem Statement

The objective of this task is to identify potential online occurrences
of a person from a given reference image and provide a way to verify
that the collected evidence has not been modified after recording.

The system therefore combines:

- Reverse image search
- Face detection
- Face encoding
- Face comparison
- Candidate ranking
- Evidence generation
- SHA-256 hashing
- Blockchain storage
- Tamper detection

---

## System Architecture

    text
                 Reference Image
                        |
                        v
                Face Detection
                        |
                        v
                 Face Encoding
                        |
                        v
              Reverse Image Search
                        |
                        v
             Social Media Candidates
                        |
                        v
              Candidate Image Download
                        |
                        v
                 Face Comparison
                        |
                        v
                Candidate Scoring
                        |
                        v
                 Evidence JSON
                        |
                        v
                  SHA-256 Hash
                        |
                        v
                 Blockchain Record
                        |
                        v
              Integrity Verification
                        |
                        v
                Tampering Detection

1. Clone the repository
    bash
git clone <https://github.com/mohammedatif23/HHGOA-task-3>
cd HH-GOA-TASK3

2. Create a virtual environment
py -3.11 -m venv venv

3. Activate the environment
source venv/Scripts/activate

4. Install dependencies
pip install -r requirements.txt

5. Configure API key

6. Run the project
python main.py