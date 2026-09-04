import os
import sys
import tempfile
import requests
import face_recognition


# ============================================================
# CONFIGURATION
# ============================================================

MATCH_THRESHOLD = 0.60

DEFAULT_REFERENCE = "samples/test.JPG"
DEFAULT_CANDIDATE = "samples/test.JPG"


# ============================================================
# LOAD IMAGE
# ============================================================

def load_image(source):
    """
    Load an image from either:
    1. A local file path
    2. An HTTP/HTTPS URL
    """

    # --------------------------------------------------------
    # Local image
    # --------------------------------------------------------

    if not source.startswith(("http://", "https://")):

        if not os.path.exists(source):
            raise FileNotFoundError(
                f"Image not found: {source}"
            )

        print(f"Loading local image: {source}")

        return face_recognition.load_image_file(source)


    # --------------------------------------------------------
    # Remote image
    # --------------------------------------------------------

    print(f"Downloading candidate image:")
    print(source)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0 Safari/537.36"
        )
    }

    response = requests.get(
        source,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    content_type = response.headers.get(
        "Content-Type",
        ""
    ).lower()

    if "image" not in content_type:

        raise ValueError(
            "The URL did not return an image.\n"
            f"Content-Type: {content_type}"
        )

    # Save temporarily
    suffix = ".jpg"

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temp_file:

        temp_file.write(response.content)
        temp_path = temp_file.name

    try:

        print("✓ Candidate image downloaded")

        image = face_recognition.load_image_file(
            temp_path
        )

        return image

    finally:

        if os.path.exists(temp_path):
            os.remove(temp_path)


# ============================================================
# GENERATE FACE ENCODING
# ============================================================

def get_face_encoding(image, image_name):
    """
    Detect faces and generate face encodings.
    """

    print(f"\nDetecting faces in {image_name}...")

    locations = face_recognition.face_locations(
        image
    )

    print(
        f"Faces detected: {len(locations)}"
    )

    if len(locations) == 0:

        return None, locations

    encodings = face_recognition.face_encodings(
        image,
        locations
    )

    return encodings, locations


# ============================================================
# COMPARE FACES
# ============================================================

def compare_faces(
    reference_encodings,
    candidate_encodings
):
    """
    Compare candidate faces against the reference face.

    If multiple faces are present in the candidate image,
    the closest face is used.
    """

    best_distance = None
    best_index = None

    for index, candidate_encoding in enumerate(
        candidate_encodings
    ):

        distance = face_recognition.face_distance(
            reference_encodings,
            candidate_encoding
        )[0]

        if (
            best_distance is None
            or distance < best_distance
        ):

            best_distance = float(distance)
            best_index = index

    if best_distance is None:

        return {
            "match": False,
            "distance": None,
            "face_index": None
        }

    is_match = best_distance <= MATCH_THRESHOLD

    return {
        "match": bool(is_match),
        "distance": best_distance,
        "face_index": best_index
    }


# ============================================================
# PRINT RESULT
# ============================================================

def print_result(
    reference_count,
    candidate_count,
    result
):

    print("\n")
    print("=" * 60)
    print("                 VERIFICATION RESULT")
    print("=" * 60)

    print(
        f"\nReference faces : {reference_count}"
    )

    print(
        f"Candidate faces : {candidate_count}"
    )

    if result["distance"] is None:

        print("\nFace distance   : N/A")
        print("Result          : ❌ NO MATCH")

    else:

        print(
            f"\nFace distance   : "
            f"{result['distance']:.4f}"
        )

        print(
            f"Threshold       : "
            f"{MATCH_THRESHOLD:.2f}"
        )

        print(
            f"Closest face    : "
            f"Face #{result['face_index'] + 1}"
        )

        if result["match"]:

            print(
                "\nResult          : ✓ POTENTIAL MATCH"
            )

        else:

            print(
                "\nResult          : ✗ NO MATCH"
            )

    print("\n" + "=" * 60)


# ============================================================
# MAIN VERIFICATION FUNCTION
# ============================================================

def verify_candidate(
    reference_source,
    candidate_source
):

    print("=" * 60)
    print("       HH GOA TASK 3 - CANDIDATE VERIFICATION")
    print("=" * 60)

    # --------------------------------------------------------
    # Reference image
    # --------------------------------------------------------

    print("\n[1] REFERENCE IMAGE")
    print("-" * 60)

    reference_image = load_image(
        reference_source
    )

    reference_encodings, reference_locations = (
        get_face_encoding(
            reference_image,
            "reference image"
        )
    )

    if not reference_encodings:

        raise ValueError(
            "No face detected in the reference image."
        )

    if len(reference_encodings) != 1:

        raise ValueError(
            "Reference image must contain exactly "
            "one face."
        )

    print(
        "✓ Reference face encoding generated"
    )

    # --------------------------------------------------------
    # Candidate image
    # --------------------------------------------------------

    print("\n[2] CANDIDATE IMAGE")
    print("-" * 60)

    candidate_image = load_image(
        candidate_source
    )

    candidate_encodings, candidate_locations = (
        get_face_encoding(
            candidate_image,
            "candidate image"
        )
    )

    if not candidate_encodings:

        print(
            "\n❌ No face detected in candidate image."
        )

        print_result(
            len(reference_encodings),
            0,
            {
                "match": False,
                "distance": None,
                "face_index": None
            }
        )

        return

    # --------------------------------------------------------
    # Compare
    # --------------------------------------------------------

    print("\n[3] FACE COMPARISON")
    print("-" * 60)

    print(
        "Comparing candidate faces "
        "against reference..."
    )

    result = compare_faces(
        reference_encodings,
        candidate_encodings
    )

    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    print_result(
        len(reference_encodings),
        len(candidate_encodings),
        result
    )


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:

        # ----------------------------------------------------
        # Command-line support
        #
        # Usage:
        #
        # python verification/candidate_verifier.py
        #
        # OR
        #
        # python verification/candidate_verifier.py \
        # samples/reference.jpg \
        # samples/test.JPG
        #
        # OR later:
        #
        # python verification/candidate_verifier.py \
        # samples/test.JPG \
        # "https://example.com/image.jpg"
        # ----------------------------------------------------

        if len(sys.argv) >= 3:

            reference_source = sys.argv[1]
            candidate_source = sys.argv[2]

        else:

            reference_source = DEFAULT_REFERENCE
            candidate_source = DEFAULT_CANDIDATE

        verify_candidate(
            reference_source,
            candidate_source
        )

    except FileNotFoundError as error:

        print("\n❌ FILE ERROR")
        print(error)
        sys.exit(1)

    except requests.RequestException as error:

        print("\n❌ DOWNLOAD ERROR")
        print(error)
        sys.exit(1)

    except Exception as error:

        print("\n❌ ERROR")
        print(
            f"{type(error).__name__}: {error}"
        )
        sys.exit(1)