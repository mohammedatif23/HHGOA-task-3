import hashlib
import json
import os


EVIDENCE_FILE = "verification/evidence.json"
BLOCKCHAIN_FILE = "blockchain/blockchain.json"


def calculate_sha256(file_path):

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        while True:

            data = file.read(8192)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()


def load_stored_evidence_hash():

    with open(
        BLOCKCHAIN_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        blockchain = json.load(file)

    # Block 1 contains our evidence
    if len(blockchain) < 2:

        raise ValueError(
            "No evidence block found."
        )

    return blockchain[1]["evidence_hash"]


def verify_evidence():

    print("=" * 60)
    print("          HH GOA - EVIDENCE VERIFICATION")
    print("=" * 60)

    # --------------------------------------------------------
    # Check files
    # --------------------------------------------------------

    if not os.path.exists(EVIDENCE_FILE):

        print(
            f"\n❌ Evidence file not found:"
            f"\n{EVIDENCE_FILE}"
        )

        return False

    if not os.path.exists(BLOCKCHAIN_FILE):

        print(
            f"\n❌ Blockchain file not found:"
            f"\n{BLOCKCHAIN_FILE}"
        )

        return False

    # --------------------------------------------------------
    # Calculate current hash
    # --------------------------------------------------------

    print("\nCalculating current evidence hash...")

    current_hash = calculate_sha256(
        EVIDENCE_FILE
    )

    print("✓ Current hash calculated")

    # --------------------------------------------------------
    # Read blockchain hash
    # --------------------------------------------------------

    print(
        "\nReading hash stored on blockchain..."
    )

    blockchain_hash = (
        load_stored_evidence_hash()
    )

    print("✓ Blockchain hash loaded")

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    print("\n" + "-" * 60)

    print("CURRENT EVIDENCE HASH:")
    print(current_hash)

    print("\nBLOCKCHAIN EVIDENCE HASH:")
    print(blockchain_hash)

    print("-" * 60)

    # --------------------------------------------------------
    # Compare
    # --------------------------------------------------------

    if current_hash == blockchain_hash:

        print(
            "\n✓ HASH MATCH"
        )

        print(
            "✓ EVIDENCE INTEGRITY VERIFIED"
        )

        print(
            "\nThe evidence has not changed "
            "since it was recorded."
        )

        return True

    else:

        print(
            "\n❌ HASH MISMATCH"
        )

        print(
            "❌ TAMPERING DETECTED"
        )

        print(
            "\nThe evidence file is different "
            "from the version recorded on the blockchain."
        )

        return False


if __name__ == "__main__":

    verify_evidence()

    print("\n" + "=" * 60)