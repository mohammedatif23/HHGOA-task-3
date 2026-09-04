import subprocess
import sys


def run_step(title, command):
    print("\n")
    print("=" * 65)
    print(title)
    print("=" * 65)

    result = subprocess.run(
        [sys.executable] + command
    )

    if result.returncode != 0:

        print("\n❌ STEP FAILED")
        print(f"Command: {' '.join(command)}")

        sys.exit(result.returncode)

    print("\n✓ STEP COMPLETED")


def main():

    print("\n")
    print("=" * 65)
    print("          HH GOA TASK 3 - COMPLETE PIPELINE")
    print("=" * 65)

    # --------------------------------------------------------
    # STEP 1
    # Reverse image search + face verification
    # --------------------------------------------------------

    run_step(
        "STEP 1/3 - REVERSE IMAGE SEARCH",
        [
            "search/reverse_search.py"
        ]
    )

    # --------------------------------------------------------
    # STEP 2
    # Blockchain evidence storage
    # --------------------------------------------------------

    run_step(
        "STEP 2/3 - BLOCKCHAIN EVIDENCE STORAGE",
        [
            "blockchain/evidence_blockchain.py"
        ]
    )

    # --------------------------------------------------------
    # STEP 3
    # Evidence integrity verification
    # --------------------------------------------------------

    run_step(
        "STEP 3/3 - EVIDENCE INTEGRITY VERIFICATION",
        [
            "verification/verify_evidence.py"
        ]
    )

    # --------------------------------------------------------
    # COMPLETE
    # --------------------------------------------------------

    print("\n")
    print("=" * 65)
    print("                 PIPELINE COMPLETE")
    print("=" * 65)

    print("\n✓ Reverse image search completed")
    print("✓ Face verification completed")
    print("✓ Evidence generated")
    print("✓ Evidence recorded on blockchain")
    print("✓ Evidence integrity verified")

    print("\nYour HH GOA Task 3 pipeline is ready.")


if __name__ == "__main__":
    main()