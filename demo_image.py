"""
Demonstration of LSB Image Steganography

This script demonstrates all features of the image steganography module:
- B1: Basic LSB encoding/decoding
- B2: Multi-bit capacity options (1, 2, 3 bits per pixel)
- Image loading/saving
- Capacity calculation
- Image comparison

Run this to see everything in action!
"""

import image_stego
import os


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_create_test_image():
    """Create a test image for demonstrations."""
    print_section("Creating Test Images")

    # Create test images directory if it doesn't exist
    os.makedirs('test_images', exist_ok=True)

    # Create different sized test images
    sizes = [
        (256, 256, 'test_images/small_image.png'),
        (512, 512, 'test_images/medium_image.png'),
        (1024, 768, 'test_images/large_image.png'),
    ]

    for width, height, path in sizes:
        image_stego.create_test_image(width, height, path)
        print(f"Created: {path} ({width}x{height})")

    print("\n✓ Test images created in 'test_images/' directory")
    return 'test_images/medium_image.png'


def demo_image_capacity():
    """Demonstrate capacity calculation."""
    print_section("1. Image Capacity Calculator")

    test_image = 'test_images/medium_image.png'

    print(f"\nAnalyzing: {test_image}\n")

    # Check capacity for different bit settings
    for bits in [1, 2, 3]:
        capacity = image_stego.get_image_capacity(test_image, bits_per_pixel=bits)

        print(f"--- Using {bits} bit(s) per pixel ---")
        print(f"  Image dimensions: {capacity['image_dimensions']}")
        print(f"  Total pixels: {capacity['total_pixels']:,}")
        print(f"  Maximum message size: {capacity['max_bytes']:,} bytes "
              f"({capacity['max_characters']:,} characters)")
        print()

    print("💡 Key insight: Using more bits per pixel = more capacity!")
    print("   But also = more visible changes to the image")


def demo_basic_lsb():
    """Demonstrate basic LSB encoding and decoding."""
    print_section("2. Basic LSB Steganography (B1)")

    cover_image = 'test_images/medium_image.png'
    stego_image = 'test_images/stego_basic.png'
    secret_message = "This is a secret message hidden in the image!"

    print(f"\nCover image: {cover_image}")
    print(f"Secret message: '{secret_message}'")
    print(f"Message length: {len(secret_message)} characters")

    # === ENCODING ===
    print("\n--- ENCODING ---")
    print("Using 1 bit per pixel (most secure, least capacity)")

    result = image_stego.encode_lsb(
        image_path=cover_image,
        message=secret_message,
        output_path=stego_image,
        bits_per_pixel=1  # Default: modify only 1 LSB
    )

    print(f"\n✓ Encoding successful!")
    print(f"  Stego image saved to: {result['output_path']}")
    print(f"  Message bits: {result['message_bits']}")
    print(f"  Header bits: {result['header_bits']} (stores message length)")
    print(f"  Total bits encoded: {result['total_bits_encoded']}")
    print(f"  Pixels modified: {result['pixels_modified']:,}")
    print(f"  Capacity used: {result['capacity_used_percent']:.2f}%")
    print(f"  Channel used: {result['channel_used']}")

    # === DECODING ===
    print("\n--- DECODING ---")

    decoded_message = image_stego.decode_lsb(
        stego_image_path=stego_image,
        bits_per_pixel=1  # Must match encoding!
    )

    print(f"Decoded message: '{decoded_message}'")

    # Verify
    if decoded_message == secret_message:
        print("\n✓ SUCCESS: Decoded message matches original!")
    else:
        print("\n✗ ERROR: Messages don't match!")

    return cover_image, stego_image


def demo_multi_bit_capacity():
    """Demonstrate B2: User-controlled capacity (1, 2, or 3 bits)."""
    print_section("3. Multi-Bit Capacity (B2)")

    cover_image = 'test_images/medium_image.png'

    # Create a longer message to show capacity benefits
    long_message = "The quick brown fox jumps over the lazy dog. " * 10
    print(f"\nLong message to encode: {len(long_message)} characters\n")

    # Test different bit settings
    for bits in [1, 2, 3]:
        print(f"--- Testing {bits} bit(s) per pixel ---")

        stego_path = f'test_images/stego_{bits}bit.png'

        try:
            result = image_stego.encode_lsb_variable(
                image_path=cover_image,
                message=long_message,
                output_path=stego_path,
                bits_per_pixel=bits
            )

            print(f"✓ Encoding successful with {bits} bit(s)")
            print(f"  Capacity used: {result['capacity_used_percent']:.2f}%")
            print(f"  Pixels modified: {result['pixels_modified']:,}")

            # Decode to verify
            decoded = image_stego.decode_lsb_variable(stego_path, bits_per_pixel=bits)

            if decoded == long_message:
                print(f"  ✓ Decoding successful")
            else:
                print(f"  ✗ Decoding failed")

        except ValueError as e:
            print(f"✗ Failed: {e}")

        print()

    print("📊 Summary:")
    print("  1 bit/pixel: Lowest capacity, most invisible")
    print("  2 bits/pixel: Balanced (recommended)")
    print("  3 bits/pixel: Highest capacity, more visible")


def demo_image_comparison():
    """Compare original and stego images."""
    print_section("4. Image Comparison (Visual Impact)")

    cover_image = 'test_images/medium_image.png'

    print("\nComparing original vs. stego images with different bit settings:\n")

    for bits in [1, 2, 3]:
        stego_image = f'test_images/stego_{bits}bit.png'

        if os.path.exists(stego_image):
            comparison = image_stego.compare_images(cover_image, stego_image)

            print(f"--- {bits} bit(s) per pixel ---")
            print(f"  Max pixel difference: {comparison['max_difference']}")
            print(f"  Mean pixel difference: {comparison['mean_difference']:.4f}")
            print(f"  Pixels changed: {comparison['pixels_changed']:,} "
                  f"({comparison['change_percentage']:.2f}%)")
            print(f"  Imperceptible to human eye: {comparison['imperceptible']}")
            print()

    print("💡 Key insight:")
    print("  - 1 bit changes: Max difference = 1 (completely invisible)")
    print("  - 2 bit changes: Max difference = 3 (nearly invisible)")
    print("  - 3 bit changes: Max difference = 7 (may be slightly visible)")


def demo_simple_api():
    """Demonstrate the simplified convenience API."""
    print_section("5. Simple API (Easiest to Use)")

    cover_image = 'test_images/small_image.png'
    message = "This is a test message using the simple API!"

    print(f"\nUsing the simplified hide_message() and extract_message() functions\n")

    # Test different quality settings
    qualities = ['high', 'standard', 'fast']

    for quality in qualities:
        stego_path = f'test_images/stego_{quality}.png'

        print(f"--- Quality: {quality.upper()} ---")

        # Hide message
        result = image_stego.hide_message(
            image_path=cover_image,
            message=message,
            output_path=stego_path,
            quality=quality
        )

        print(f"  Bits per pixel: {result['bits_per_pixel']}")
        print(f"  Capacity used: {result['capacity_used_percent']:.2f}%")

        # Extract message
        extracted = image_stego.extract_message(stego_path, quality=quality)

        if extracted == message:
            print(f"  ✓ Round-trip successful")
        else:
            print(f"  ✗ Round-trip failed")

        print()

    print("Quality settings explained:")
    print("  'high'     = 1 bit/pixel (best quality, least capacity)")
    print("  'standard' = 2 bits/pixel (balanced - recommended)")
    print("  'fast'     = 3 bits/pixel (most capacity, quality reduced)")


def demo_header_system():
    """Demonstrate the message length header system."""
    print_section("6. Header System (How We Know Message Length)")

    print("\nThe header system allows us to decode without knowing message length!\n")

    # Create messages of different lengths
    messages = [
        "Short",
        "Medium length message here",
        "Very long message that contains a lot of text and information " * 5
    ]

    cover_image = 'test_images/medium_image.png'

    for i, message in enumerate(messages):
        stego_path = f'test_images/stego_header_test_{i}.png'

        print(f"--- Message {i+1}: {len(message)} characters ---")

        # Encode
        result = image_stego.encode_lsb(cover_image, message, stego_path)

        print(f"  Message bits: {result['message_bits']}")
        print(f"  Header bits: {result['header_bits']} (stores message length)")
        print(f"  Total encoded: {result['total_bits_encoded']}")

        # Decode (no need to specify message length!)
        decoded = image_stego.decode_lsb(stego_path)

        if decoded == message:
            print(f"  ✓ Correctly decoded {len(decoded)} characters")
        else:
            print(f"  ✗ Decoding failed")

        print()

    print("💡 How it works:")
    print("  1. First 32 bits = header storing message length")
    print("  2. Remaining bits = actual message")
    print("  3. Decoder reads header first to know when to stop")
    print("  4. This prevents reading garbage data beyond the message")


def demo_capacity_limits():
    """Demonstrate what happens when message is too large."""
    print_section("7. Capacity Limits and Error Handling")

    # Use very small image
    small_image = 'test_images/small_image.png'  # 256x256

    capacity = image_stego.get_image_capacity(small_image, bits_per_pixel=1)
    max_chars = capacity['max_characters']

    print(f"\nImage: {small_image}")
    print(f"Maximum capacity: {max_chars} characters (with 1 bit/pixel)\n")

    # Try to encode message that's too large
    huge_message = "X" * (max_chars + 1000)  # Way too big!

    print(f"Attempting to encode {len(huge_message)} characters...")
    print("(This is larger than the image capacity)\n")

    try:
        image_stego.encode_lsb(small_image, huge_message, 'test_images/fail.png')
        print("✗ Should have failed!")
    except ValueError as e:
        print(f"✓ Correctly caught error:")
        print(f"  {str(e)[:100]}...")

    print("\n💡 Solutions when message is too large:")
    print("  1. Use a larger cover image")
    print("  2. Use more bits per pixel (2 or 3 instead of 1)")
    print("  3. Compress or shorten the message")
    print("  4. Or combine with encryption (coming in next section!)")


def demo_real_world_example():
    """Show a realistic usage scenario."""
    print_section("8. Real-World Example: Sending Hidden Messages")

    print("\nScenario: Alice wants to send Bob a secret message")
    print("by posting an innocent-looking image on social media.\n")

    # Alice's side
    print("--- ALICE (Sender) ---")

    original_image = 'test_images/medium_image.png'
    alice_message = "The package will arrive at the drop point tomorrow at noon. Confirm receipt."
    stego_image = 'test_images/alice_photo.png'

    print(f"Alice's innocent photo: {original_image}")
    print(f"Alice's secret message: '{alice_message}'")

    # Alice encodes
    result = image_stego.hide_message(
        image_path=original_image,
        message=alice_message,
        output_path=stego_image,
        quality='standard'
    )

    print(f"\nAlice posts the image: {stego_image}")
    print(f"  Image looks completely normal!")
    print(f"  Only {result['capacity_used_percent']:.3f}% of capacity used")
    print(f"  Changes are invisible to the human eye")

    # Public sees this
    print("\n--- PUBLIC (Everyone else) ---")
    print("Public sees: Just a normal photo, nothing suspicious")

    # Bob's side
    print("\n--- BOB (Receiver) ---")
    print("Bob downloads the image and extracts the message...")

    bob_decoded = image_stego.extract_message(stego_image, quality='standard')

    print(f"Bob's decoded message: '{bob_decoded}'")

    if bob_decoded == alice_message:
        print("\n✓ Secure communication successful!")
        print("  - Public saw nothing suspicious")
        print("  - Only Bob (who knew to look) found the message")
        print("  - Image appears completely normal")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 70)
    print("  LSB IMAGE STEGANOGRAPHY DEMONSTRATION")
    print("  B1: Basic LSB + B2: Multi-bit Capacity")
    print("=" * 70)

    try:
        # Create test images
        test_image = demo_create_test_image()

        # Run all demos
        demo_image_capacity()
        cover, stego = demo_basic_lsb()
        demo_multi_bit_capacity()
        demo_image_comparison()
        demo_simple_api()
        demo_header_system()
        demo_capacity_limits()
        demo_real_world_example()

        print("\n" + "=" * 70)
        print("  ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
        print("=" * 70)

        print("\nQuick Start Guide:")
        print("-" * 70)
        print("from image_stego import hide_message, extract_message")
        print("")
        print("# Hide message in image:")
        print("hide_message('photo.png', 'Secret!', 'stego.png')")
        print("")
        print("# Extract message:")
        print("message = extract_message('stego.png')")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
