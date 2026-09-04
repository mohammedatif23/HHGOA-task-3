import hashlib


def calculate_sha256(file_path):
    """
    Calculate the SHA-256 hash of a file.
    """

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        while True:

            data = file.read(8192)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()


def calculate_text_sha256(text):
    """
    Calculate SHA-256 hash of text.
    """

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


if __name__ == "__main__":

    file_path = "verification/evidence.json"

    print("=" * 55)
    print("             SHA-256 EVIDENCE HASH")
    print("=" * 55)

    hash_value = calculate_sha256(
        file_path
    )

    print("\nFile:")
    print(file_path)

    print("\nSHA-256:")
    print(hash_value)

    print("\nHash length:")
    print(len(hash_value))

    print("\n✓ Hash generated successfully")