import os
import json
import hashlib

from dotenv import load_dotenv
from web3 import Web3


EVIDENCE_FILE = "verification/evidence.json"
RECORD_FILE = "blockchain/blockchain_record.json"

SEPOLIA_CHAIN_ID = 11155111


def calculate_sha256(filepath):
    sha256 = hashlib.sha256()

    with open(filepath, "rb") as file:
        while True:
            data = file.read(8192)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()


def load_record():
    if not os.path.exists(RECORD_FILE):
        raise FileNotFoundError(
            f"Blockchain record not found: {RECORD_FILE}"
        )

    with open(RECORD_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def main():

    print("=" * 60)
    print("BLOCKCHAIN EVIDENCE VERIFICATION")
    print("=" * 60)

    load_dotenv()

    rpc_url = os.getenv("ALCHEMY_RPC_URL")

    if not rpc_url:
        print("ERROR: ALCHEMY_RPC_URL is missing.")
        return 1

    # --------------------------------------------------
    # 1. Calculate current evidence hash
    # --------------------------------------------------

    print("\n[1] Calculating current evidence hash...")

    if not os.path.exists(EVIDENCE_FILE):
        print(f"ERROR: {EVIDENCE_FILE} not found.")
        return 1

    current_hash = calculate_sha256(EVIDENCE_FILE)

    print(f"    Current SHA-256:")
    print(f"    {current_hash}")

    # --------------------------------------------------
    # 2. Load blockchain record
    # --------------------------------------------------

    print("\n[2] Loading blockchain record...")

    try:
        record = load_record()
    except Exception as error:
        print(f"ERROR: {error}")
        return 1

    stored_hash = record.get("evidence_sha256")
    transaction_hash = record.get("transaction_hash")
    chain_id = record.get("chain_id")

    if not stored_hash or not transaction_hash:
        print("ERROR: Blockchain record is incomplete.")
        return 1

    print(f"    Network: {record.get('network')}")
    print(f"    Transaction: {transaction_hash}")

    # --------------------------------------------------
    # 3. Verify network
    # --------------------------------------------------

    print("\n[3] Connecting to Ethereum Sepolia...")

    web3 = Web3(Web3.HTTPProvider(rpc_url))

    if not web3.is_connected():
        print("ERROR: Could not connect to Ethereum.")
        return 1

    actual_chain_id = web3.eth.chain_id

    print(f"    Connected: True")
    print(f"    Chain ID: {actual_chain_id}")

    if actual_chain_id != SEPOLIA_CHAIN_ID:
        print("ERROR: Connected to the wrong blockchain.")
        return 1

    if chain_id != SEPOLIA_CHAIN_ID:
        print("ERROR: Stored record is not for Sepolia.")
        return 1

    # --------------------------------------------------
    # 4. Read actual transaction from blockchain
    # --------------------------------------------------

    print("\n[4] Reading transaction from Ethereum...")

    try:
        transaction = web3.eth.get_transaction(
            transaction_hash
        )

        receipt = web3.eth.get_transaction_receipt(
            transaction_hash
        )

    except Exception as error:
        print(f"ERROR: Could not retrieve transaction.")
        print(error)
        return 1

    if receipt.status != 1:
        print("ERROR: Blockchain transaction failed.")
        return 1

    print("    Transaction found.")
    print(f"    Block: {receipt.blockNumber}")
    print("    Status: SUCCESS")

    # --------------------------------------------------
    # 5. Extract hash from transaction data
    # --------------------------------------------------

    print("\n[5] Extracting evidence hash from blockchain...")

    blockchain_data = transaction.get("input")

    if not blockchain_data:
        print("ERROR: Transaction contains no evidence data.")
        return 1

    # Web3.py may return transaction input as bytes.
    # Convert it to hexadecimal text before comparing.
    if isinstance(blockchain_data, bytes):
        blockchain_hash = blockchain_data.hex()
    else:
        blockchain_data = str(blockchain_data)

        if blockchain_data.startswith("0x"):
            blockchain_hash = blockchain_data[2:]
        else:
            blockchain_hash = blockchain_data

    print("    On-chain SHA-256:")
    print(f"    {blockchain_hash}")

    # --------------------------------------------------
    # 6. Compare hashes
    # --------------------------------------------------

    print("\n[6] Comparing hashes...")

    if current_hash.lower() == blockchain_hash.lower():

        print("\n" + "=" * 60)
        print("HASH MATCH")
        print("EVIDENCE INTEGRITY VERIFIED")
        print("=" * 60)

        print("\nBlockchain transaction:")
        print(
            f"https://sepolia.etherscan.io/tx/"
            f"{transaction_hash}"
        )

        return 0

    else:

        print("\n" + "=" * 60)
        print("HASH MISMATCH")
        print("TAMPERING DETECTED")
        print("=" * 60)

        print("\nExpected hash:")
        print(f"{blockchain_hash}")

        print("\nCurrent file hash:")
        print(f"{current_hash}")

        return 1


if __name__ == "__main__":
    exit_code = main()
    raise SystemExit(exit_code) 