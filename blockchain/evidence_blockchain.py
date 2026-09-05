import os
import json
import hashlib
from datetime import datetime, timezone

from dotenv import load_dotenv
from web3 import Web3


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

load_dotenv()

RPC_URL = os.getenv("ALCHEMY_RPC_URL")
PRIVATE_KEY = os.getenv("BLOCKCHAIN_PRIVATE_KEY")

EVIDENCE_FILE = "verification/evidence.json"
RECORD_FILE = "blockchain/blockchain_record.json"

SEPOLIA_CHAIN_ID = 11155111


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def calculate_sha256(filepath):
    """Calculate SHA-256 hash of a file."""

    sha256 = hashlib.sha256()

    with open(filepath, "rb") as file:
        while True:
            data = file.read(8192)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()


def load_evidence():
    """Load evidence JSON."""

    if not os.path.exists(EVIDENCE_FILE):
        raise FileNotFoundError(
            f"Evidence file not found: {EVIDENCE_FILE}"
        )

    with open(EVIDENCE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def connect_to_blockchain():
    """Connect to Ethereum Sepolia."""

    if not RPC_URL:
        raise RuntimeError(
            "ALCHEMY_RPC_URL is missing from .env"
        )

    if not PRIVATE_KEY:
        raise RuntimeError(
            "BLOCKCHAIN_PRIVATE_KEY is missing from .env"
        )

    web3 = Web3(Web3.HTTPProvider(RPC_URL))

    if not web3.is_connected():
        raise RuntimeError(
            "Could not connect to Ethereum Sepolia."
        )

    if web3.eth.chain_id != SEPOLIA_CHAIN_ID:
        raise RuntimeError(
            f"Wrong network. Expected {SEPOLIA_CHAIN_ID}, "
            f"got {web3.eth.chain_id}"
        )

    return web3


# ---------------------------------------------------------
# Main blockchain operation
# ---------------------------------------------------------

def main():

    print("=" * 60)
    print("ETHEREUM SEPOLIA EVIDENCE RECORD")
    print("=" * 60)

    # 1. Check evidence
    print("\n[1] Loading evidence...")

    evidence = load_evidence()

    print("    Evidence loaded successfully.")

    # 2. Calculate evidence hash
    print("\n[2] Calculating SHA-256 hash...")

    evidence_hash = calculate_sha256(EVIDENCE_FILE)

    print(f"    Evidence SHA-256:")
    print(f"    {evidence_hash}")

    # 3. Connect to Sepolia
    print("\n[3] Connecting to Ethereum Sepolia...")

    web3 = connect_to_blockchain()

    print("    Connected: True")
    print(f"    Chain ID: {web3.eth.chain_id}")
    print(f"    Latest block: {web3.eth.block_number}")

    # 4. Load wallet
    account = web3.eth.account.from_key(PRIVATE_KEY)

    wallet_address = account.address

    print("\n[4] Blockchain account:")
    print(f"    {wallet_address}")

    # 5. Check balance
    balance = web3.eth.get_balance(wallet_address)
    balance_eth = web3.from_wei(balance, "ether")

    print(f"    Balance: {balance_eth} Sepolia ETH")

    if balance == 0:
        raise RuntimeError(
            "Wallet has no Sepolia ETH. "
            "Get test ETH before sending the transaction."
        )

    # 6. Prepare transaction data
    #
    # We store the evidence hash directly inside the
    # transaction's input data.
    #
    # This makes the transaction itself the tamper-evident
    # blockchain record.

    print("\n[5] Preparing blockchain transaction...")

    transaction_data = web3.to_bytes(
        hexstr="0x" + evidence_hash
    )

    nonce = web3.eth.get_transaction_count(
        wallet_address,
        "pending"
    )

    latest_block = web3.eth.get_block("latest")

    base_fee = latest_block.get("baseFeePerGas")

    if base_fee is not None:
        max_priority_fee = web3.to_wei(1, "gwei")

        max_fee_per_gas = (
            base_fee * 2 + max_priority_fee
        )

        gas_price = None
    else:
        gas_price = web3.eth.gas_price
        max_priority_fee = None
        max_fee_per_gas = None

    transaction = {
        "chainId": SEPOLIA_CHAIN_ID,
        "nonce": nonce,
        "to": wallet_address,
        "value": 0,
        "data": transaction_data,
    }

    if gas_price is not None:

        transaction["gasPrice"] = gas_price

    else:

        transaction["maxPriorityFeePerGas"] = (
            max_priority_fee
        )

        transaction["maxFeePerGas"] = (
            max_fee_per_gas
        )

    # Estimate gas
    estimated_gas = web3.eth.estimate_gas(
        transaction
    )

    transaction["gas"] = estimated_gas

    print(f"    Nonce: {nonce}")
    print(f"    Gas estimate: {estimated_gas}")

    # 7. Sign transaction
    print("\n[6] Signing transaction...")

    signed_transaction = web3.eth.account.sign_transaction(
        transaction,
        PRIVATE_KEY
    )

    # 8. Send transaction
    print("\n[7] Sending transaction to Ethereum Sepolia...")

    tx_hash = web3.eth.send_raw_transaction(
        signed_transaction.raw_transaction
    )

    tx_hash_hex = tx_hash.hex()

    print(f"    Transaction hash:")
    print(f"    {tx_hash_hex}")

    # 9. Wait for confirmation
    print("\n[8] Waiting for blockchain confirmation...")

    receipt = web3.eth.wait_for_transaction_receipt(
        tx_hash,
        timeout=180
    )

    if receipt.status != 1:
        raise RuntimeError(
            "Blockchain transaction failed."
        )

    print("    Transaction confirmed.")
    print(f"    Block number: {receipt.blockNumber}")

    # 10. Explorer URL
    explorer_url = (
        "https://sepolia.etherscan.io/tx/"
        + tx_hash_hex
    )

    print("\n[9] Blockchain explorer:")
    print(f"    {explorer_url}")

    # 11. Save local blockchain record
    #
    # The local file is only a convenient record of
    # what was submitted. The actual authoritative
    # record is the Ethereum transaction.

    blockchain_record = {
        "network": "Ethereum Sepolia",
        "chain_id": SEPOLIA_CHAIN_ID,
        "wallet_address": wallet_address,
        "evidence_file": EVIDENCE_FILE,
        "evidence_sha256": evidence_hash,
        "transaction_hash": tx_hash_hex,
        "block_number": receipt.blockNumber,
        "explorer_url": explorer_url,
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    os.makedirs(
        os.path.dirname(RECORD_FILE),
        exist_ok=True
    )

    with open(
        RECORD_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            blockchain_record,
            file,
            indent=4
        )

    print("\n[10] Local blockchain record saved:")
    print(f"     {RECORD_FILE}")

    print("\n" + "=" * 60)
    print("BLOCKCHAIN RECORD SUCCESSFUL")
    print("=" * 60)


if __name__ == "__main__":
    main()