import face_recognition

REFERENCE_IMAGE = "samples/reference.jpg"
TEST_IMAGE = "samples/test.JPG"

print("=" * 55)
print("HH GOA TASK 3 - FACE MATCHING")
print("=" * 55)

# -----------------------------------------
# Load reference image
# -----------------------------------------

print("\n[1] Loading reference image...")

reference_image = face_recognition.load_image_file(REFERENCE_IMAGE)
reference_locations = face_recognition.face_locations(reference_image)

print(f"    Faces detected: {len(reference_locations)}")

if len(reference_locations) != 1:
    print("❌ Reference image must contain exactly one face.")
    exit()

reference_encoding = face_recognition.face_encodings(
    reference_image,
    reference_locations
)[0]

print("    ✓ Reference face encoding generated")


# -----------------------------------------
# Load test image
# -----------------------------------------

print("\n[2] Loading test image...")

test_image = face_recognition.load_image_file(TEST_IMAGE)
test_locations = face_recognition.face_locations(test_image)

print(f"    Faces detected: {len(test_locations)}")

if len(test_locations) == 0:
    print("❌ No face found in test image.")
    exit()

test_encodings = face_recognition.face_encodings(
    test_image,
    test_locations
)

print(f"    ✓ Generated {len(test_encodings)} test encoding(s)")


# -----------------------------------------
# Compare faces
# -----------------------------------------

print("\n[3] Comparing faces...")

for i, test_encoding in enumerate(test_encodings):

    distance = face_recognition.face_distance(
        [reference_encoding],
        test_encoding
    )[0]

    # Convert distance into a simple similarity score
    similarity = max(0, (1 - distance) * 100)

    match = face_recognition.compare_faces(
        [reference_encoding],
        test_encoding,
        tolerance=0.6
    )[0]

    print(f"\n    Face #{i + 1}")
    print(f"    Face distance : {distance:.4f}")
    print(f"    Similarity    : {similarity:.2f}%")

    if match:
        print("    RESULT        : ✓ MATCH")
    else:
        print("    RESULT        : ✗ NO MATCH")


print("\n" + "=" * 55)
print("FACE MATCHING COMPLETE")
print("=" * 55)