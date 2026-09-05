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