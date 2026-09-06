# HH GOA TASK 3 — Face Identification & Blockchain Evidence Verification

## Overview

This project implements an end-to-end face identification and evidence verification pipeline.

The system:

1. Detects and encodes a face from a reference image.
2. Performs a genuine reverse-image search using Google Lens through SerpApi.
3. Finds potential social-media matches.
4. Downloads candidate images when available.
5. Compares the reference face with faces found in candidate images.
6. Ranks potential matches.
7. Generates an evidence report.
8. Calculates a SHA-256 hash of the evidence.
9. Records the evidence hash on the Ethereum Sepolia testnet.
10. Reads the blockchain transaction back from Ethereum.
11. Verifies whether the current evidence still matches the original blockchain record.
12. Detects tampering when the evidence is modified.

No website or hosting is required.

---

## Problem Statement

The objective is to identify potential online occurrences of a person from a given reference image and create a tamper-evident record of the collected evidence.

The project combines:

- Face detection
- Face encoding
- Reverse-image search
- Social-media candidate discovery
- Face comparison
- Candidate ranking
- Evidence generation
- SHA-256 hashing
- Ethereum blockchain storage
- Blockchain verification
- Tamper detection

---

## System Architecture

```text
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
                Candidate Ranking
                        |
                        v
                  Evidence JSON
                        |
                        v
                   SHA-256
                        |
                        v
             Ethereum Sepolia
                        |
                        v
              Blockchain Transaction
                        |
                        v
             Blockchain Verification
                        |
                        v
               Tampering Detection

## Installation

1. Clone the repository
git clone https://github.com/mohammedatif23/HHGOA-task-3.git
cd HH-GOA-TASK3

2. Create a virtual environment

Windows:

py -3.11 -m venv venv

3. Activate the virtual environment

Git Bash:
source venv/Scripts/activate
PowerShell:
.\venv\Scripts\Activate.ps1

4. Install dependencies
pip install -r requirements.txt
Configuration

Create a .env file in the project root.

SERPAPI_KEY=YOUR_SERPAPI_API_KEY

ALCHEMY_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/YOUR_ALCHEMY_API_KEY



Reverse Image Search

The reverse-image search module uses SerpApi's Google Lens engine.

The reference image is submitted for a genuine reverse-image search.

The system does not use hardcoded social-media search results.

Potential candidates are collected from supported social platforms such as:

YouTube
Instagram
Facebook
Reddit
TikTok
X/Twitter
LinkedIn
Pinterest

Candidate images are downloaded when possible and compared against the reference face.

Face Verification

The project uses the face recognition library.

The reference image is:

samples/test.JPG

The system:

Detects faces.
Generates a face encoding.
Detects faces in candidate images.
Calculates face distance.
Uses the best candidate face for comparison.
Assigns a match level.

Lower face distance indicates greater similarity.

The result is treated as a potential match and should not be interpreted as definitive proof of identity.

Evidence Generation

The reverse-search module creates:

verification/evidence.json

The evidence contains information about the selected candidate, including relevant search and face-comparison information.

The evidence file is hashed using SHA-256.

Evidence JSON
      |
      v
   SHA-256
      |
      v
64-character hexadecimal hash
Ethereum Blockchain Record

The evidence hash is recorded on the Ethereum Sepolia testnet.

Network
Ethereum Sepolia
Chain ID
11155111

The project sends a zero-value transaction from the test wallet to itself.

The SHA-256 evidence hash is stored in the transaction input data.

The resulting transaction information is saved locally in:

blockchain/blockchain_record.json

The local record contains:

Network
Chain ID
Wallet address
Evidence SHA-256
Transaction hash
Block number
Sepolia explorer URL
Timestamp

The authoritative blockchain record is the Ethereum Sepolia transaction.

Blockchain Verification

The verification module is:

verification/verify_evidence.py

It performs the following:

Current evidence.json
        |
        v
Calculate SHA-256
        |
        v
Connect to Ethereum Sepolia
        |
        v
Read recorded transaction
        |
        v
Extract on-chain evidence hash
        |
        v
Compare hashes

If the hashes match:

HASH MATCH
EVIDENCE INTEGRITY VERIFIED

If they do not match:

HASH MISMATCH
TAMPERING DETECTED
Running the Complete Pipeline

Make sure the virtual environment is active and .env is configured.

Run:

python main.py

The pipeline performs:

Reverse image search
Candidate face verification
Evidence generation
Ethereum Sepolia blockchain recording
Blockchain integrity verification

A successful run should finish with:

HASH MATCH
EVIDENCE INTEGRITY VERIFIED

PIPELINE COMPLETE
Tamper Detection Test

The system can detect changes made to the evidence after the blockchain record was created.

Original evidence:

Original evidence
        |
        v
     SHA-256 A
        |
        v
Ethereum Sepolia

If the evidence is modified:

Modified evidence
        |
        v
     SHA-256 B
        |
        v
Compare with SHA-256 A
        |
        v
HASH MISMATCH
TAMPERING DETECTED

The original evidence can then be restored and verified again.

Limitations:
Reverse-image search results depend on the search provider and available indexed content.
Some social-media images cannot be downloaded because of access restrictions.
Face recognition can produce false positives and false negatives.
A face similarity score is not definitive proof of a person's identity.
The system identifies potential matches rather than legally establishing identity.
Ethereum Sepolia is a testnet and is not intended for production evidence storage.
Blockchain storage records the evidence hash rather than storing the complete image on-chain.
Privacy and Security

The system should only be used with images and information that you are permitted to process.

Do not commit secrets to GitHub.

The following files and credentials are private:

.env
Private keys
API keys
Secret recovery phrases
Wallet passwords

Disclaimer:
This project is a technical demonstration for Hacker House Goa Task #3.

Face similarity results should be treated as potential matches, not definitive identity claims.

The blockchain record provides evidence integrity verification, not proof that the underlying information is true.

TEAM: 
       MOHAMMED EHTESHAMUDDIN ATIF.
       MOOSA VIQAR SHARIF.
       FURQAN ALI.