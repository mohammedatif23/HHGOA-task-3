import os
from urllib.parse import urlparse

import serpapi
from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

API_KEY = os.getenv("SERPAPI_KEY")

if not API_KEY:
    raise RuntimeError(
        "SERPAPI_KEY not found.\n"
        "Create a .env file in the project root and add:\n"
        "SERPAPI_KEY=YOUR_API_KEY"
    )


IMAGE_PATH = "samples/test.JPG"


# Social-media domains we want to identify
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
# HELPER: IDENTIFY SOCIAL PLATFORM
# ============================================================

def get_social_platform(url):
    """
    Determine which social-media platform a URL belongs to.
    """

    if not url:
        return None

    try:
        hostname = urlparse(url).hostname

        if not hostname:
            return None

        hostname = hostname.lower()

        # Remove www.
        if hostname.startswith("www."):
            hostname = hostname[4:]

        for domain, platform in SOCIAL_DOMAINS.items():

            if hostname == domain or hostname.endswith("." + domain):
                return platform

    except Exception:
        return None

    return None


# ============================================================
# REVERSE IMAGE SEARCH
# ============================================================

def reverse_image_search(image_path):

    print("\n" + "=" * 55)
    print("              REVERSE IMAGE SEARCH")
    print("=" * 55)

    # --------------------------------------------------------
    # Check image
    # --------------------------------------------------------

    if not os.path.exists(image_path):
        raise FileNotFoundError(
            f"\nImage not found:\n{image_path}\n\n"
            "Make sure the image exists inside the samples folder."
        )

    print("\nImage:")
    print(f"  {image_path}")

    # --------------------------------------------------------
    # Create SerpApi client
    # --------------------------------------------------------

    print("\nConnecting to SerpApi...")

    client = serpapi.Client(api_key=API_KEY)

    print("✓ Connected")

    # --------------------------------------------------------
    # Upload image
    # --------------------------------------------------------

    print("\nUploading image...")

    upload = client.upload_image(image_path)

    image_id = upload.get("image_id")

    if not image_id:
        print("\nUpload response:")
        print(upload)

        raise RuntimeError(
            "Image upload failed: no image_id returned."
        )

    print("✓ Image uploaded")
    print(f"  Image ID: {image_id}")

    # --------------------------------------------------------
    # Google Lens search
    # --------------------------------------------------------

    print("\nSearching with Google Lens...")

    results = client.search({
        "engine": "google_lens",
        "image_id": image_id,
    })

    print("✓ Google Lens search completed")

    return results


# ============================================================
# EXTRACT SOCIAL-MEDIA CANDIDATES
# ============================================================

def extract_social_candidates(results):

    candidates = []

    # Google Lens visual matches
    visual_matches = results.get("visual_matches", [])

    for result in visual_matches:

        link = result.get("link", "")

        platform = get_social_platform(link)

        if not platform:
            continue

        candidate = {
            "platform": platform,
            "title": result.get("title", "Unknown"),
            "link": link,
            "source": result.get("source", ""),
            "thumbnail": result.get("thumbnail"),
            "image": result.get("image"),
            "exact_match": result.get("exact_matches", False),
            "position": result.get("position"),
        }

        candidates.append(candidate)

    return candidates


# ============================================================
# PRINT ALL VISUAL MATCHES
# ============================================================

def print_visual_matches(results):

    visual_matches = results.get("visual_matches", [])

    print("\n" + "=" * 55)
    print("                 VISUAL MATCHES")
    print("=" * 55)

    print(f"\nTotal visual matches: {len(visual_matches)}")

    if not visual_matches:
        print("\n❌ No visual matches returned.")

        return

    for i, result in enumerate(visual_matches[:10], 1):

        title = result.get("title", "Unknown")
        link = result.get("link", "No link")

        print(f"\n--- Result {i} ---")

        print(f"Title : {title}")
        print(f"Link  : {link}")

        source = result.get("source")

        if source:
            print(f"Source: {source}")

        exact = result.get("exact_matches")

        if exact is not None:
            print(
                f"Exact Match: "
                f"{'YES' if exact else 'NO'}"
            )


# ============================================================
# PRINT SOCIAL-MEDIA CANDIDATES
# ============================================================

def print_social_candidates(candidates):

    print("\n" + "=" * 55)
    print("             SOCIAL MEDIA CANDIDATES")
    print("=" * 55)

    if not candidates:

        print("\n❌ No social-media candidates found.")

        return

    print(
        f"\n✓ Found {len(candidates)} "
        "social-media candidate(s)"
    )

    for i, candidate in enumerate(candidates, 1):

        print(f"\n[{i}] {candidate['platform']}")

        print(
            f"    Title       : "
            f"{candidate['title']}"
        )

        print(
            f"    URL         : "
            f"{candidate['link']}"
        )

        if candidate["source"]:
            print(
                f"    Source      : "
                f"{candidate['source']}"
            )

        print(
            f"    Exact Match : "
            f"{'YES' if candidate['exact_match'] else 'NO'}"
        )

        if candidate["position"] is not None:
            print(
                f"    Lens Rank   : "
                f"{candidate['position']}"
            )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    try:

        # ----------------------------------------------------
        # Run reverse-image search
        # ----------------------------------------------------

        results = reverse_image_search(IMAGE_PATH)

        # ----------------------------------------------------
        # Show result sections
        # ----------------------------------------------------

        print("\n" + "=" * 55)
        print("             RESULT INFORMATION")
        print("=" * 55)

        print("\nAvailable result sections:")

        for key in results.keys():
            print(f"  • {key}")

        # ----------------------------------------------------
        # Print visual matches
        # ----------------------------------------------------

        print_visual_matches(results)

        # ----------------------------------------------------
        # Extract social-media candidates
        # ----------------------------------------------------

        candidates = extract_social_candidates(results)

        # ----------------------------------------------------
        # Print social candidates
        # ----------------------------------------------------

        print_social_candidates(candidates)

        # ----------------------------------------------------
        # Summary
        # ----------------------------------------------------

        print("\n" + "=" * 55)
        print("                    SUMMARY")
        print("=" * 55)

        print(
            f"\nVisual matches : "
            f"{len(results.get('visual_matches', []))}"
        )

        print(
            f"Social candidates : "
            f"{len(candidates)}"
        )

        if candidates:

            print(
                "\n✓ Reverse-image search successfully "
                "returned social-media candidates."
            )

        else:

            print(
                "\n⚠ No social-media candidates were found "
                "in the returned visual matches."
            )

        print("\n" + "=" * 55)

    except Exception as error:

        print("\n" + "=" * 55)
        print("                    ERROR")
        print("=" * 55)

        print(f"\n{type(error).__name__}: {error}")

        print("\n" + "=" * 55)

        raise