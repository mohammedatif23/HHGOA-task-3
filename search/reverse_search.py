import os
import json
from urllib.parse import urlparse

import requests
import serpapi
import face_recognition
from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

API_KEY = os.getenv("SERPAPI_KEY")

if not API_KEY:
    raise RuntimeError(
        "SERPAPI_KEY not found in .env"
    )

INPUT_IMAGE = "samples/test.JPG"

OUTPUT_DIR = "verification/downloaded"

REPORT_PATH = "verification/evidence.json"

MATCH_THRESHOLD = 0.60


# ============================================================
# SOCIAL MEDIA DOMAINS
# ============================================================

SOCIAL_DOMAINS = {
    "instagram.com": "Instagram",
    "facebook.com": "Facebook",
    "tiktok.com": "TikTok",
    "twitter.com": "X",
    "x.com": "X",
    "youtube.com": "YouTube",
    "linkedin.com": "LinkedIn",
    "pinterest.com": "Pinterest",
    "reddit.com": "Reddit",
}


# ============================================================
# GET SOCIAL PLATFORM
# ============================================================

def get_social_platform(url):

    if not url:
        return None

    try:

        hostname = urlparse(url).hostname

        if not hostname:
            return None

        hostname = hostname.lower()

        if hostname.startswith("www."):
            hostname = hostname[4:]

        for domain, platform in SOCIAL_DOMAINS.items():

            if (
                hostname == domain
                or hostname.endswith("." + domain)
            ):
                return platform

    except Exception:
        pass

    return None


# ============================================================
# REVERSE IMAGE SEARCH
# ============================================================

def reverse_image_search(image_path):

    print("\n" + "=" * 60)
    print("              GOOGLE LENS SEARCH")
    print("=" * 60)

    if not os.path.exists(image_path):

        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    client = serpapi.Client(
        api_key=API_KEY
    )

    print("\nUploading image...")

    upload = client.upload_image(
        image_path
    )

    image_id = upload.get(
        "image_id"
    )

    if not image_id:

        raise RuntimeError(
            f"Image upload failed: {upload}"
        )

    print("✓ Image uploaded")

    print("\nSearching Google Lens...")

    results = client.search({
        "engine": "google_lens",
        "image_id": image_id
    })

    print("✓ Search completed")

    return results


# ============================================================
# EXTRACT SOCIAL CANDIDATES
# ============================================================

def extract_candidates(results):

    candidates = []

    visual_matches = results.get(
        "visual_matches",
        []
    )

    for result in visual_matches:

        link = result.get(
            "link",
            ""
        )

        platform = get_social_platform(
            link
        )

        if not platform:
            continue

        candidate = {

            "platform": platform,

            "title": result.get(
                "title",
                "Unknown"
            ),

            "url": link,

            "source": result.get(
                "source",
                ""
            ),

            "image_url": result.get(
                "image",
                ""
            ),

            "thumbnail_url": result.get(
                "thumbnail",
                ""
            ),

            "exact_match": bool(
                result.get(
                    "exact_matches",
                    False
                )
            ),

            "lens_position": result.get(
                "position"
            )
        }

        candidates.append(
            candidate
        )

    return candidates


# ============================================================
# DOWNLOAD CANDIDATE IMAGE
# ============================================================

def download_candidate_image(
    image_url,
    output_path
):

    if not image_url:
        return False

    try:

        response = requests.get(
            image_url,
            timeout=20,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/131 Safari/537.36"
                )
            }
        )

        response.raise_for_status()

        content_type = response.headers.get(
            "Content-Type",
            ""
        ).lower()

        if "image" not in content_type:

            print(
                "    ⚠ URL did not return an image"
            )

            return False

        os.makedirs(
            os.path.dirname(output_path),
            exist_ok=True
        )

        with open(
            output_path,
            "wb"
        ) as file:

            file.write(
                response.content
            )

        return True

    except Exception as error:

        print(
            f"    ⚠ Download failed: {error}"
        )

        return False


# ============================================================
# GET REFERENCE FACE
# ============================================================

def get_reference_encoding(
    image_path
):

    image = face_recognition.load_image_file(
        image_path
    )

    locations = face_recognition.face_locations(
        image
    )

    if len(locations) != 1:

        raise ValueError(
            "Input image must contain exactly "
            "one detectable face."
        )

    encodings = face_recognition.face_encodings(
        image,
        locations
    )

    if not encodings:

        raise ValueError(
            "Could not generate face encoding "
            "for input image."
        )

    return encodings[0]


# ============================================================
# VERIFY CANDIDATE
# ============================================================

def verify_candidate(
    reference_encoding,
    candidate_path
):

    try:

        image = face_recognition.load_image_file(
            candidate_path
        )

        locations = face_recognition.face_locations(
            image
        )

        if not locations:

            return {
                "status": "NO_FACE",
                "faces_detected": 0,
                "distance": None,
                "match": False,
                "confidence": "NO MATCH"
            }

        encodings = face_recognition.face_encodings(
            image,
            locations
        )

        if not encodings:

            return {
                "status": "ENCODING_FAILED",
                "faces_detected": len(locations),
                "distance": None,
                "match": False,
                "confidence": "NO MATCH"
            }

        best_distance = None

        # Compare reference face against every
        # detected face in the candidate image.
        for encoding in encodings:

            distance = face_recognition.face_distance(
                [reference_encoding],
                encoding
            )[0]

            distance = float(distance)

            if (
                best_distance is None
                or distance < best_distance
            ):

                best_distance = distance

        # ----------------------------------------------------
        # Determine whether it passes the threshold
        # ----------------------------------------------------

        match = (
            best_distance <= MATCH_THRESHOLD
        )

        # ----------------------------------------------------
        # Confidence classification
        # ----------------------------------------------------

        if best_distance <= 0.45:

            confidence = "HIGH"

        elif best_distance <= 0.55:

            confidence = "MEDIUM"

        elif best_distance <= 0.60:

            confidence = "LOW"

        else:

            confidence = "NO MATCH"

        return {

            "status": "CHECKED",

            "faces_detected": len(
                locations
            ),

            "distance": best_distance,

            "match": bool(match),

            "confidence": confidence
        }

    except Exception as error:

        return {

            "status": "ERROR",

            "faces_detected": 0,

            "distance": None,

            "match": False,

            "confidence": "NO MATCH",

            "error": str(error)
        }


# ============================================================
# CALCULATE CANDIDATE SCORE
# ============================================================

def calculate_score(
    candidate,
    verification
):

    score = 0.0

    # --------------------------------------------------------
    # Exact Lens match
    # --------------------------------------------------------

    if candidate["exact_match"]:

        score += 0.30

    # --------------------------------------------------------
    # Face match
    # --------------------------------------------------------

    if verification["match"]:

        score += 0.50

    # --------------------------------------------------------
    # Better face distance
    # --------------------------------------------------------

    distance = verification.get(
        "distance"
    )

    if distance is not None:

        similarity_score = max(
            0,
            1 - distance
        )

        score += (
            similarity_score * 0.20
        )

    return round(
        min(score, 1.0),
        4
    )


# ============================================================
# PROCESS CANDIDATES
# ============================================================

def process_candidates(
    candidates,
    reference_encoding
):

    results = []

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    for index, candidate in enumerate(
        candidates[:10],
        start=1
    ):

        print("\n" + "-" * 60)

        print(
            f"CANDIDATE {index}"
        )

        print(
            f"Platform : "
            f"{candidate['platform']}"
        )

        print(
            f"Title    : "
            f"{candidate['title']}"
        )

        print(
            f"URL      : "
            f"{candidate['url']}"
        )

        # ----------------------------------------------------
        # Prefer actual image.
        # Fall back to thumbnail.
        # ----------------------------------------------------

        image_url = (
            candidate["image_url"]
            or candidate["thumbnail_url"]
        )

        candidate_file = os.path.join(
            OUTPUT_DIR,
            f"candidate_{index}.jpg"
        )

        print(
            "\nDownloading candidate image..."
        )

        downloaded = download_candidate_image(
            image_url,
            candidate_file
        )

        verification = {

            "status":
                "IMAGE_DOWNLOAD_FAILED",

            "faces_detected": 0,

            "distance": None,

            "match": False,

            "confidence": "NO MATCH"
        }

        # ----------------------------------------------------
        # Face verification
        # ----------------------------------------------------

        if downloaded:

            print(
                "✓ Candidate image downloaded"
            )

            print(
                "Comparing face..."
            )

            verification = verify_candidate(
                reference_encoding,
                candidate_file
            )

            if verification["match"]:

                print(
                    f"✓ POTENTIAL FACE MATCH "
                    f"({verification['confidence']} confidence)"
                )

            else:

                print(
                    f"✗ Face did not match "
                    f"({verification['confidence']})"
                )

        else:

            print(
                "✗ Candidate image could not be downloaded"
            )

        # ----------------------------------------------------
        # Calculate score
        # ----------------------------------------------------

        score = calculate_score(
            candidate,
            verification
        )

        print(
            f"Candidate score: "
            f"{score:.4f}"
        )

        # ----------------------------------------------------
        # Create result
        # ----------------------------------------------------

        result = {

            "rank": index,

            "platform": candidate[
                "platform"
            ],

            "title": candidate[
                "title"
            ],

            "url": candidate[
                "url"
            ],

            "source": candidate[
                "source"
            ],

            "lens_position": candidate[
                "lens_position"
            ],

            "lens_exact_match":
                candidate[
                    "exact_match"
                ],

            "candidate_image": (
                candidate_file
                if downloaded
                else None
            ),

            "verification":
                verification,

            "score": score
        }

        results.append(
            result
        )

    return results


# ============================================================
# SAVE EVIDENCE REPORT
# ============================================================

def save_evidence_report(
    results
):

    os.makedirs(
        os.path.dirname(REPORT_PATH),
        exist_ok=True
    )

    report = {

        "input_image":
            INPUT_IMAGE,

        "match_threshold":
            MATCH_THRESHOLD,

        "candidates_checked":
            len(results),

        "results":
            results
    }

    with open(
        REPORT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4
        )

    print(
        f"\n✓ Evidence report saved:"
    )

    print(
        f"  {REPORT_PATH}"
    )


# ============================================================
# PRINT FINAL RESULTS
# ============================================================

def print_final_results(
    results
):

    print("\n")

    print("=" * 60)

    print(
        "                 FINAL RESULTS"
    )

    print("=" * 60)

    if not results:

        print(
            "\n❌ No candidates available."
        )

        return

    # Highest score first

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    for index, result in enumerate(
        results,
        start=1
    ):

        verification = result[
            "verification"
        ]

        print(
            f"\n#{index} "
            f"{result['platform']}"
        )

        print(
            f"Title       : "
            f"{result['title']}"
        )

        print(
            f"URL         : "
            f"{result['url']}"
        )

        print(
            f"Lens Match  : "
            f"{'YES' if result['lens_exact_match'] else 'NO'}"
        )

        print(
            f"Faces       : "
            f"{verification['faces_detected']}"
        )

        if verification[
            "distance"
        ] is not None:

            print(
                f"Face Distance: "
                f"{verification['distance']:.4f}"
            )

        print(
            f"Face Match  : "
            f"{'YES' if verification['match'] else 'NO'}"
        )

        print(
            f"Confidence  : "
            f"{verification.get('confidence', 'N/A')}"
        )

        print(
            f"Final Score : "
            f"{result['score']:.4f}"
        )

    # --------------------------------------------------------
    # Best candidate
    # --------------------------------------------------------

    best = results[0]

    print("\n" + "=" * 60)

    print(
        "                 BEST CANDIDATE"
    )

    print("=" * 60)

    print(
        f"\nPlatform : "
        f"{best['platform']}"
    )

    print(
        f"Title    : "
        f"{best['title']}"
    )

    print(
        f"URL      : "
        f"{best['url']}"
    )

    print(
        f"Score    : "
        f"{best['score']:.4f}"
    )

    best_verification = (
        best["verification"]
    )

    print(
        f"Face Distance : "
        f"{best_verification.get('distance')}"
    )

    print(
        f"Confidence    : "
        f"{best_verification.get('confidence', 'N/A')}"
    )

    if best_verification["match"]:

        print(
            "\n✓ POTENTIAL MATCH FOUND"
        )

        print(
            f"  Confidence: "
            f"{best_verification.get('confidence')}"
        )

    else:

        print(
            "\n⚠ No verified face match "
            "among the candidates."
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("\n")

    print("=" * 60)

    print(
        "       HH GOA TASK 3 - END-TO-END SEARCH"
    )

    print("=" * 60)

    # --------------------------------------------------------
    # Step 1: Load reference face
    # --------------------------------------------------------

    print(
        "\n[1/4] Loading input face..."
    )

    reference_encoding = (
        get_reference_encoding(
            INPUT_IMAGE
        )
    )

    print(
        "✓ Face encoding generated"
    )

    # --------------------------------------------------------
    # Step 2: Reverse search
    # --------------------------------------------------------

    print(
        "\n[2/4] Running reverse-image search..."
    )

    lens_results = reverse_image_search(
        INPUT_IMAGE
    )

    # --------------------------------------------------------
    # Step 3: Extract candidates
    # --------------------------------------------------------

    print(
        "\n[3/4] Extracting social-media candidates..."
    )

    candidates = extract_candidates(
        lens_results
    )

    print(
        f"✓ {len(candidates)} "
        "social-media candidate(s) found"
    )

    # --------------------------------------------------------
    # Step 4: Verify candidates
    # --------------------------------------------------------

    print(
        "\n[4/4] Verifying candidates..."
    )

    verified_results = process_candidates(
        candidates,
        reference_encoding
    )

    # --------------------------------------------------------
    # Save evidence
    # --------------------------------------------------------

    save_evidence_report(
        verified_results
    )

    # --------------------------------------------------------
    # Final output
    # --------------------------------------------------------

    print_final_results(
        verified_results
    )

    print("\n")

    print("=" * 60)

    print(
        "                PIPELINE COMPLETE"
    )

    print("=" * 60)