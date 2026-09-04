import hashlib
import json
import os
import time


EVIDENCE_FILE = "verification/evidence.json"
BLOCKCHAIN_FILE = "blockchain/blockchain.json"


class Block:

    def __init__(
        self,
        index,
        timestamp,
        evidence_hash,
        previous_hash
    ):
        self.index = index
        self.timestamp = timestamp
        self.evidence_hash = evidence_hash
        self.previous_hash = previous_hash

        self.hash = self.calculate_hash()

    def calculate_hash(self):

        data = (
            str(self.index)
            + str(self.timestamp)
            + self.evidence_hash
            + self.previous_hash
        )

        return hashlib.sha256(
            data.encode("utf-8")
        ).hexdigest()

    def to_dict(self):

        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "evidence_hash": self.evidence_hash,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }


class EvidenceBlockchain:

    def __init__(self):
        self.chain = [
            self.create_genesis_block()
        ]

    def create_genesis_block(self):

        return Block(
            0,
            time.time(),
            "GENESIS",
            "0"
        )

    def get_latest_block(self):
        return self.chain[-1]

    def add_evidence(self, evidence_hash):

        previous = self.get_latest_block()

        block = Block(
            len(self.chain),
            time.time(),
            evidence_hash,
            previous.hash
        )

        self.chain.append(block)

        return block

    def is_valid(self):

        for i in range(1, len(self.chain)):

            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.calculate_hash():
                return False

            if current.previous_hash != previous.hash:
                return False

        return True

    def save(self, path):

        os.makedirs(
            os.path.dirname(path),
            exist_ok=True
        )

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                [block.to_dict() for block in self.chain],
                file,
                indent=4
            )


def calculate_file_hash(path):

    sha256 = hashlib.sha256()

    with open(path, "rb") as file:

        while True:

            data = file.read(8192)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()


if __name__ == "__main__":

    print("=" * 60)
    print("       HH GOA - REAL EVIDENCE BLOCKCHAIN")
    print("=" * 60)

    # --------------------------------------------------------
    # Check evidence
    # --------------------------------------------------------

    if not os.path.exists(EVIDENCE_FILE):

        raise FileNotFoundError(
            f"Evidence file not found: {EVIDENCE_FILE}\n"
            "Run the reverse-search pipeline first."
        )

    # --------------------------------------------------------
    # Calculate REAL evidence hash
    # --------------------------------------------------------

    print("\nCalculating evidence SHA-256...")

    evidence_hash = calculate_file_hash(
        EVIDENCE_FILE
    )

    print("✓ Evidence hash generated")

    print("\nSHA-256:")
    print(evidence_hash)

    # --------------------------------------------------------
    # Create blockchain
    # --------------------------------------------------------

    blockchain = EvidenceBlockchain()

    print("\n✓ Genesis block created")

    # --------------------------------------------------------
    # Add REAL evidence
    # --------------------------------------------------------

    block = blockchain.add_evidence(
        evidence_hash
    )

    print("\n✓ Real evidence added to blockchain")

    # --------------------------------------------------------
    # Display block
    # --------------------------------------------------------

    print("\nBlock information:")

    print(
        json.dumps(
            block.to_dict(),
            indent=4
        )
    )

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    print("\nBlockchain validation:")

    if blockchain.is_valid():

        print("✓ BLOCKCHAIN VALID")

    else:

        print("❌ BLOCKCHAIN INVALID")

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    blockchain.save(
        BLOCKCHAIN_FILE
    )

    print(
        f"\n✓ Blockchain saved to:"
    )

    print(
        BLOCKCHAIN_FILE
    )

    print("\n" + "=" * 60)